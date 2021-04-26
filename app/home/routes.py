# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from app.base import constants
from app.base.routes import requires_auth, session
from app.home import blueprint
from flask import render_template, request, jsonify, redirect
from jinja2 import TemplateNotFound
# import flask_restful
import pymysql
from datetime import datetime


config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password':'mysql',
    'database': 'mydb',
    'charset': 'utf8'
}


def get_id():
    conn = pymysql.connect(**config)

    try:
        with conn.cursor() as cur:
            sql = "SELECT user_no, user_category FROM users WHERE email = %s"
            cur.execute(sql, [session[constants.JWT_PAYLOAD]['email']])

        user_no = cur.fetchone()

        with conn.cursor() as cur:
            sql = "SELECT max(order_id) FROM orders WHERE user_no=%s"
            cur.execute(sql, [user_no[0]])

        order_id = cur.fetchone()

    finally:
        data_list = [user_no[0], user_no[1], order_id[0]]

        conn.close()

    return data_list

  
###############################################
###############     메인     ##################
###############################################

@blueprint.route('/index_login')
def index():
    # 현재 로그인한 user_no
    user_no = get_id()

    db = pymysql.connect(**config)
    cur = db.cursor()
    
    sql = "SELECT * from festival"
    cur.execute(sql)

    data_list = cur.fetchall()

    user_data = session[constants.JWT_PAYLOAD]['name']

    return render_template('index_login.html', data_list=data_list, user_data=user_data, user_no=user_no[0])


@blueprint.route('/jan_festival')
def index2_2():
    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = "SELECT A.order_id,A.total_price,B.festival_id,B.festival_name from orders A INNER JOIN festival B ON A.user_no=B.user_no"
    cur.execute(sql)

    data_list = cur.fetchall()
    
    
    return jsonify(data_list)


###############################################
###############    관리자    ##################
###############################################
# 관리자 화면
@blueprint.route('/admin')
def admin_festival_using():
    
    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = '''SELECT A.user_name,A.phone_number,B.company_name,B.festival_name,B.period,B.location,B.url,B.festival_id
        from users A INNER JOIN festival B
        ON A.user_no=B.user_no
        '''
    cur.execute(sql)

    data_list = cur.fetchall()
    return render_template('admin.html', data_list=data_list)


# 관리자 측면에서 전체 페스티벌
@blueprint.route('/admin')
def admin_index():
    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = "SELECT * from festival"
    cur.execute(sql)

    data_list = cur.fetchall()

    return render_template('admin.html', segment='index2', data_list=data_list)


# 관리자 화면 데이터 삭제
@blueprint.route('/admin_delete', methods=['POST'])
def admin_festival_delete():
    json_data = request.get_json()
    db = pymysql.connect(**config)
    cur = db.cursor()
    print(json_data)
    data_store_id = {}
    sql = "SELECT store_id from store where festival_id=%s"
    cur.execute(sql, [json_data['festival_id']])
    data_store_id = cur.fetchall()

    for i in data_store_id:
        sql = '''Delete from orders where store_id=%s'''
        cur.execute(sql, [i])

    for i in data_store_id:
        sql = '''Delete from menu where store_id=%s'''
        cur.execute(sql, [i])

    sql = '''Delete from store where festival_id=%s'''
    cur.execute(sql, [json_data['festival_id']])

    sql = '''Delete from festival where festival_id=%s'''
    cur.execute(sql, [json_data['festival_id']])

    db.commit()

    return jsonify(result="success", result2=json_data)


###############################################
###########         고객          #############
###############################################
# 가게 리스트 출력
@blueprint.route('/storeList/<string:f_id>')
def store_list(f_id):
    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = '''select store_name, store_id, store_description, location_number
             from store
             where festival_id=%s'''
    cur.execute(sql, [f_id])

    data_list = cur.fetchall()
    return render_template('storeList.html', segment='storelist', data_list=data_list)


# 가게마다 메뉴 리스트 출력
@blueprint.route('/storeMenuList/<int:id>')
def menulist(id):
    data_list = get_menu2(id)
    return render_template('storeMenuList.html', segment='storemenulist', data_list=data_list)


# 주문페이지 출력
@blueprint.route('/order')
@requires_auth
def order_get():
    conn = pymysql.connect(**config)
    data = get_id()

    try:
        with conn.cursor() as cursor:
            sql = "SELECT total_price FROM orders WHERE order_id=%s"
            cursor.execute(sql, [data[2]])

        data_list = cursor.fetchall()

    finally:
        conn.close()

    return render_template('order.html', data_list=data_list)


# 고객 주문 상세 페이지
@blueprint.route('/order_sate')
@requires_auth
def credit_get():
    conn = pymysql.connect(**config)
    data = get_id()

    try:
        with conn.cursor() as cursor:
            sql = '''SELECT b.store_name, b.location_number FROM orders a LEFT JOIN store b 
                        ON a.store_id = b.store_id WHERE a.user_no=%s'''
            cursor.execute(sql, [data[0]])

        store_data = cursor.fetchall()

        with conn.cursor() as cursor:
            sql = "SELECT total_price FROM orders WHERE user_no=%s"
            cursor.execute(sql, [data[0]])

        price_data = cursor.fetchall()

        with conn.cursor() as cursor:
            sql = '''SELECT order_state FROM orders WHERE order_id=%s'''
            cursor.execute(sql, [data[2]])

        order_state = cursor.fetchall()

    finally:
        data_list = []
        for i, j, k in zip(store_data, price_data, order_state):
            data_list.append(i + j + k)

        conn.close()
        print(data_list)
    return render_template('order_sate.html', data_list=data_list)


# 메뉴 가져오는 함수
def get_menu2(id):
    db = pymysql.connect(**config)

    cur = db.cursor()
    sql = '''select menu_id, menu_name, menu_price from menu where store_id=%s'''

    cur.execute(sql, id)
    data_list = cur.fetchall()

    a = list(data_list)
    a.insert(len(a), id)
    a = tuple(a)

    return data_list


# 주문 페이지에서 POST 함수
@blueprint.route('/order_post', methods=['POST'])
@requires_auth
def order_post():
    json_data = request.get_json()
    conn = pymysql.connect(**config)
    data = get_id()

    try:
        with conn.cursor() as cursor:
            sql = "UPDATE orders SET requests=%s WHERE order_id=%s"
            cursor.execute(sql, [json_data['request_text'], data[2]])

        conn.commit()

        with conn.cursor() as cursor:
            sql = "UPDATE users SET phone_number=%s WHERE user_no=%s"
            cursor.execute(sql, [json_data['phone_number'], data[0]])

        conn.commit()

    finally:
        conn.close()

    return jsonify(result="success", result2=json_data)
    

# 주문 데이터 DB에 INSERT
@blueprint.route('/order_insert', methods=['POST'])
def order_insert():
    req_data = request.get_json()
    data = get_id()
    # DB algo
    db = pymysql.connect(**config)
    cur = db.cursor()

    sum = 0
    cnt = 0
    k = req_data.keys()
    kk = list(k)
    main_key = kk[0]

    for d in req_data[main_key]:
        for key, value in d.items():
            # 전체 수량 합하기
            for i in value:
                cnt += int(i)

            cur.execute("select menu_price from menu where menu_id=%s", key)
            a = cur.fetchall()

            # 전체 가격 합하기
            for i in a:
                for j in i:
                    sum += int(j) * int(value)

    sql = "insert into orders (user_no, store_id, total_qty, total_price) values(%s, %s, %s, %s)"
    cur.execute(sql, [data[0], main_key, cnt, sum])
    db.commit()

    db.close()

    newID = cur.lastrowid
    # print(newID, type(newID))
    orderdetail_insert(main_key, req_data, newID)

    return render_template('storeMenuList.html', segment='cartlist')


# 주문 데이터 DB에 INSERT
def orderdetail_insert(store_id, data, newID):
    db = pymysql.connect(**config)
    cur = db.cursor()
    cnt = 0
    price = 0
    for d in data[store_id]:
        for key, value in d.items():
            # 수량 뽑아내기
            for i in value:
                cnt = int(i)
 

            cur.execute("select menu_price from menu where menu_id=%s", key)
            print(type(key))
            a = cur.fetchall()

            # 가격 뽑아내기
            for i in a:
                for j in i:
                    price = int(j)
                    sql = "insert into order_detail (order_id, menu_id, food_price, food_qty) values(%s, %s, %s, %s)"
                    cur.execute(sql,
                                (int(newID), int(key), int(price), int(cnt)))

    db.commit()
    db.close()
    return "success"


###############################################
###########        주최자         #############
###############################################
# 현재 접속한 주최자의 페스티벌에 등록된 가게 리스트
@blueprint.route('/manager')
def jan_festival_using():
    data = get_id()
    cur_id = data[0]

    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = '''SELECT A.user_name,A.phone_number,B.company_name,B.festival_name,B.period,B.location,B.url,B.festival_id
        from users A INNER JOIN festival B
        ON A.user_no=B.user_no
        where A.user_no=%s
        '''
    cur.execute(sql, [cur_id])

    data_list = cur.fetchall()

    sql = "SELECT festival_id from festival where user_no=%s"
    cur.execute(sql, [cur_id])
    festival_id = cur.fetchall()
    data_list2 = []

    for i in festival_id:

        sql = "SELECT * from store where festival_id=%s"
        cur.execute(sql, [i[0]])
        data_list2 += cur.fetchall()

    return render_template('manager.html', data_list=data_list, data_list2=data_list2)


# 주최자 페스티벌 등록 함수
@blueprint.route('/manager_festival_insert', methods=['POST'])
def manager_festival_insert():
    json_data = request.get_json()
    data = get_id()
    usr_no = data[0]
    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = '''Insert into festival(user_no,company_name,festival_name,period,location,url,last_modify)
    values(%s,%s,%s,%s,%s,%s,%s);
    '''

    json_data['last_modify'] = str(datetime.today())
    cur.execute(sql, [
        usr_no, json_data['company_name'], json_data['festival_name'],
        json_data['period'], json_data['location'], json_data['url'],
        json_data['last_modify']
    ])

    db.commit()

    return jsonify(result="success", result2=json_data)


###############################################
###########        판매자         #############
###############################################
# 각 판매자 주문, 관리 페이지
@blueprint.route('/forSeller')
def order_detail():
    conn = pymysql.connect(**config)
    data = get_id()

    try:
        # 현재 접속한 판매자의 정보
        with conn.cursor() as cursor:
            sql = '''SELECT store_id FROM users a LEFT JOIN store b 
                        ON a.user_no=b.user_no 
                        WHERE a.user_no=%s'''
            cursor.execute(sql, [data[0]])

        data_one = cursor.fetchone()

        # 판매자에게 주문한 order list
        with conn.cursor() as cursor:
            sql = '''SELECT order_id, user_no, created_at, total_price, total_qty, payment, order_state, requests
                    FROM orders WHERE store_id=%s'''
            cursor.execute(sql, [data_one[0]])

        data_two = cursor.fetchall()

        # 주문한 유저 정보
        with conn.cursor() as cursor:
            sql = '''SELECT user_name, phone_number FROM users WHERE user_no=%s'''
            cursor.execute(sql, [data_two[0][1]])

        data_two_1 = cursor.fetchall()

        # 주문한 메뉴아이디, 수량
        with conn.cursor() as cursor:
            sql = '''SELECT menu_id, food_qty FROM order_detail WHERE order_id=%s'''
            
            if len(data_two) != 1:
                data_three = ()
                for i in range(len(data_two)):
                    cursor.execute(sql, data_two[i][0])
                    data_three += cursor.fetchall()
            else:
                cursor.execute(sql, data_two[0][0])
                data_three = cursor.fetchall()

        # 주문한 메뉴이름
        with conn.cursor() as cursor:
            sql = "SELECT menu_name FROM menu WHERE menu_id=%s"
            
            if len(data_three) != 1:
                data_four = ()
                for i in range(len(data_three)):
                    cursor.execute(sql, data_three[i][0])
                    data_four += cursor.fetchone()
        
            else:
                cursor.execute(sql, data_three[0][0])
                data_four = cursor.fetchall()

    finally:
        data_list = []
        for i, j in zip(data_two_1, data_two):
            data_list.append(i + j)

        conn.close()

    return render_template('forSeller.html', data_list=data_list, menu=data_four)


@blueprint.route('/jan_apply', methods=['GET', 'POST'])
def index2_1_1():
    db = pymysql.connect(**config)
    cur = db.cursor()
    data = get_id()

    sql = "SELECT * FROM festival LEFT OUTER JOIN users ON festival.user_no=users.user_no where users.user_no=%s"

    cur.execute(sql, [data[0]])
    data_list = cur.fetchall()
  
    return render_template('jan_apply.html', segment='index2_1_1', data_list=data_list)

    
@blueprint.route('/jyj_seller_info')
def store_info():

    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = "SELECT * from store"
    cur.execute(sql)

    data_list = cur.fetchall()

    return render_template('jyj_seller_info.html', data_list=data_list)


@blueprint.route('/jyj_seller')
def jyj_seller():
    db = pymysql.connect(**config)
    cur = db.cursor()

    data_list_two = ()

    sql = '''SELECT A.menu_name,B.total_price,B.total_qty
    from menu A INNER JOIN orders B
    ON A.store_id=B.store_id
    '''
    cur.execute(sql)
    data_list_two += cur.fetchall()  #1~4
    price = {}
    qty = {}
    menu_list = []
    for i in data_list_two:
        if (price.get(i[0]) == None):
            price[i[0]] = i[1]
            menu_list.append(i[0])
        else:
            price[i[0]] += i[1]

    for i in data_list_two:
        if (qty.get(i[0]) == None):
            qty[i[0]] = i[2]
        else:
            qty[i[0]] += i[2]

    data_list = []

    for i in menu_list:
        data_list.append([i, price[i], qty[i]])

    return render_template('jyj_seller.html', data_list=data_list)


@blueprint.route('/jyj_seller_apply')
def store_save():
    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = "SELECT festival_name from festival"
    cur.execute(sql)

    data_list = cur.fetchall()
    return render_template('jyj_seller_apply.html', data_list=data_list)


# 판매자 정보등록 
@blueprint.route('/seller_store_insert', methods=['POST'])
def myajax():

    json_data = request.get_json()
    db = pymysql.connect(**config)
    cur = db.cursor()
    data_festival_id = {}
    sql = "SELECT festival_id from festival where festival_name=%s"
    cur.execute(sql, json_data['festival_name'])
    data_festival_id = cur.fetchall()
    sql = '''Insert into store(festival_id,store_name,store_description ,contact_number,category,license_number,location_number,created_at)
    values(%s,%s,%s,%s,%s,%s,%s,%s);
    '''

    json_data['created__at'] = str(datetime.today())
    cur.execute(sql, [
        data_festival_id, json_data['store_name'],
        json_data['store_description'], json_data['contact_number'],
        json_data['category'], json_data['license_number'],
        json_data['location_number'], json_data['created__at']
    ])

    db.commit()

    return jsonify(result="success", result2=json_data)


# 판매자 정보 삭제
@blueprint.route('/seller_store_delete', methods=['POST'])
def myajax_delete():

    json_data = request.get_json()
    db = pymysql.connect(**config)
    cur = db.cursor()

    sql = '''Delete from orders where store_id=%s
    '''
    cur.execute(sql, [json_data['store_id']])
    sql = '''Delete from menu where store_id=%s
    '''
    cur.execute(sql, [json_data['store_id']])
    sql = '''Delete from store where store_id=%s
    '''
    cur.execute(sql, [json_data['store_id']])

    db.commit()

    return jsonify(result="success", result2=json_data)


#
@blueprint.route('/order_state_update', methods=['POST'])
def myajax_state_update():

    json_data = request.get_json()
    print(json_data)
    db = pymysql.connect(**config)

    data_list_one = {}
    cur = db.cursor()
    sql = "SELECT order_state from orders"
    cur.execute(sql)
    data_list_one = cur.fetchall()
    for i in data_list_one:
        if (i == '주문중', ):
            sql = '''Update orders SET order_state=%s
            where order_id=%s
            '''
            cur.execute(sql, ['주문완료', json_data['order_id']])
            db.commit()

    return jsonify(result="success", result2=json_data)


@blueprint.route('/<template>')
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/FILE.html
        return render_template(template, segment=segment)

    except TemplateNotFound:
        return render_template('page-404.html'), 404

    except:
        return render_template('page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None