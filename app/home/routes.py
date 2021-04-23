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
    'port': 13306,
    'user': 'root',
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
            sql = "SELECT order_id FROM orders WHERE user_no=%s"
            cur.execute(sql, [user_no[0]])

        order_id = cur.fetchone()

    finally:
        data_list = [user_no[0], user_no[1], order_id]

        conn.close()

    return data_list

  
# <<<------------재성-------------->>>
@blueprint.route('/jaesung_festivalList')
def index():

    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = "SELECT * from festival"
    cur.execute(sql)

    data_list = cur.fetchall()
    user_data = session[constants.JWT_PAYLOAD]['name']

    return render_template('jaesung_festivalList.html', segment='index', data_list=data_list, user_data=user_data)


# <<<------------연옥-------------->>>
@blueprint.route('/admin_index')
def index2():
    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = "SELECT * from festival"
    cur.execute(sql)

    data_list = cur.fetchall()

    return render_template('jan_festival_using.html', segment='index2', data_list=data_list)


@blueprint.route('/jan_apply', methods=['GET', 'POST'])
def index2_1_1():
    db = pymysql.connect(**config)
    cur = db.cursor()
    data = get_id()

    sql = "SELECT * FROM festival LEFT OUTER JOIN users ON festival.user_no=users.user_no where users.user_no=%s"

    cur.execute(sql, [data[0]])
    data_list = cur.fetchall()
  
    return render_template('jan_apply.html', segment='index2_1_1', data_list=data_list)


@blueprint.route('/jan_festival')
def index2_2():
    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = "SELECT A.order_id,A.total_price,B.festival_id,B.festival_name from orders A INNER JOIN festival B ON A.user_no=B.user_no"
    cur.execute(sql)

    data_list = cur.fetchall()
    
    return jsonify(data_list)


# <<<------------현주_1-------------->>>
@blueprint.route('/jan_festival_using')
def jan_festival_using():

    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = '''SELECT A.user_name,A.phone_number,B.company_name,B.festival_name,B.period,B.location,B.url,B.festival_id
        from users A INNER JOIN festival B
        ON A.user_no=B.user_no
        '''
    cur.execute(sql)

    data_list = cur.fetchall()
    return render_template('jan_festival_using.html', data_list=data_list)


@blueprint.route('/myajax_festival_delete', methods=['POST'])
def myajax_festival_delete():

    json_data = request.get_json()
    db = pymysql.connect(**config)
    cur = db.cursor()

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


@blueprint.route('/juthor_dash')
def index3():

    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = "SELECT * from festival"
    cur.execute(sql)

    data_list = cur.fetchall()

    return render_template('juthor_dash.html', segment='index3', data_list=data_list)


###############################################
########카테고리 선택 후 가게 보여주기###########
###############################################

# <<<------------현주_1-------------->>>
@blueprint.route('/juthor_category')
def category():
    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = '''select unique category, count(category) as '가게 수'
             from store
             group by category'''
    cur.execute(sql)

    data_list=[]
    list2 = []
    for list in cur.fetchall():
        list2 = []
        for v in list:
            list2.append(v)
        if list[0] == '치킨':
            list2.append("/chicken")
        elif list[0] == '분식':
            list2.append("/schoolfood")
        elif list[0] == '한식':
            list2.append("/koreanfood")
        elif list[0] == '호프점':
            list2.append("/beer")    
        data_list.append(list2)
    print(data_list)

    return render_template('juthor_category.html', segment='category', data_list=data_list)

  
@blueprint.route('/chicken')
def get_chicken():
    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = '''select store_name, store_id, store_description, location_number
             from store
             where category="치킨"'''
    cur.execute(sql)

    data_list = cur.fetchall()
    return render_template('juthor_storeList.html', segment='storelist', data_list=data_list)


@blueprint.route('/schoolfood')
def get_schoolfood():
    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = '''select store_name, store_id, store_description, location_number
             from store
             where category="분식"'''
    cur.execute(sql)

    data_list = cur.fetchall()
    return render_template('juthor_storeList.html', segment='storelist', data_list=data_list)



@blueprint.route('/koreanfood')
def get_koreanfood():
    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = '''select store_name, store_id, store_description, location_number
             from store
             where category="한식"'''
    cur.execute(sql)

    data_list = cur.fetchall()
    return render_template('juthor_storeList.html', segment='storelist', data_list=data_list)

@blueprint.route('/beer')
def get_beer():
    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = '''select store_name, store_id, store_description, location_number
             from store
             where category="호프점"'''
    cur.execute(sql)

    data_list = cur.fetchall()
    return render_template('juthor_storeList.html', segment='storelist', data_list=data_list)



@blueprint.route('/juthor_storelist')
def store_list():
    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = '''select store_name, store_id, store_description, location_number
             from store
             where category="치킨"'''
    cur.execute(sql)

    data_list = cur.fetchall()
    return render_template('juthor_storeList.html', segment='storelist', data_list=data_list)


#######################################################
#########가게 선택 후 메뉴보여주기 위한매커니즘 #########
#######################################################
@blueprint.route('/juthor_storemenulist/<int:id>')
def menulist(id):
    data_list = get_menu2(id)
    return render_template('juthor_storemenulist.html', segment='storemenulist', data_list=data_list)


def get_menu2(id):
    db = pymysql.connect(**config)

    cur = db.cursor()
    sql = '''select menu_id, menu_name, menu_price from menu where store_id=%s'''

    cur.execute(sql, id)
    data_list = cur.fetchall()

        
    a = list(data_list)
    a.insert(len(a), id)
    a = tuple(a)
    print (a)
    return data_list  


# <<<------------현재-------------->>>
@blueprint.route('/jhj_order')
@requires_auth
def order_get():
    conn = pymysql.connect(**config)
    data = get_id()

    if not data[2]:
        return redirect('/jaesung_festivalList')
    else:
        try:
            with conn.cursor() as cursor:
                sql = "SELECT total_price FROM orders WHERE order_id=%s"
                cursor.execute(sql, [data[1]])

            data_list = cursor.fetchall()

        finally:
            conn.close()

    return render_template('jhj_order.html', data_list=data_list)


@blueprint.route('/order_post', methods=['POST'])
@requires_auth
def order_post():
    json_data = request.get_json()
    conn = pymysql.connect(**config)
    data = get_id()

    try:
        with conn.cursor() as cursor:
            sql = "UPDATE orders SET requests=%s WHERE order_id=%s"
            cursor.execute(sql, [json_data['request_text'], data[1]])

        conn.commit()

        with conn.cursor() as cursor:
            sql = "UPDATE users SET phone_number=%s WHERE user_no=%s"
            cursor.execute(sql, [json_data['phone_number'], data[0]])

        conn.commit()

    finally:
        conn.close()

    return jsonify(result="success", result2=json_data)


@blueprint.route('/jhj_credit')
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
            cursor.execute(sql, [data[1]])

        order_state = cursor.fetchall()

    finally:
        data_list = []
        for i, j, k in zip(store_data, price_data,order_state):
            data_list.append(i + j + k)

        conn.close()

    return render_template('jhj_credit.html', data_list=data_list)


# <<<------------현주_2-------------->>>
@blueprint.route('/order_insert', methods=['POST'])
@requires_auth
def order_insert():
    data = request.get_json()
    data = get_id()

    # DB algo
    db = pymysql.connect(**config)
    cur = db.cursor()

    sum = 0
    cnt = 0
    k = data.keys()
    kk = list(k)
    main_key=kk[0]

    for d in data[main_key]:
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
    cur.execute(sql, [data[0]], (main_key, cnt, sum))
    db.commit()
    
    
    db.close()
    
    newID = cur.lastrowid
    print(newID, type(newID))
    orderdetail_insert(main_key, data, newID)

    return render_template('juthor_cart.html', segment='cartlist')


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
                print(cnt)

            cur.execute("select menu_price from menu where menu_id=%s", key)
            print(type(key))
            a = cur.fetchall()
            
            # 가격 뽑아내기
            for i in a:
                for j in i:
                    price = int(j)
                    sql = "insert into order_detail (order_id, menu_id, food_price, food_qty) values(%s, %s, %s, %s)"
                    cur.execute(sql, (int(newID), int(key), int(price), int(cnt)))
    
    db.commit()
    db.close()
    return "success"


# <<<-----------윤재--------------->>>
@blueprint.route('/jyj_seller_info')
@requires_auth
def store_info():

    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = "SELECT * from store"
    cur.execute(sql)

    data_list = cur.fetchall()

    return render_template('jyj_seller_info.html', data_list=data_list)


@blueprint.route('/jyj_order_detail')
@requires_auth
def order_detail():
    data = get_id()
    #  - 구매자 이름(users.user_name) one
    #  - 구매자 연락처(users.phone_number) one
    #  - 음식 이름(menu.menu_name)  two 3.store_id
    #  - 주문 시간(orders.order_time) three 1.user_id
    #  - 총 가격(orders.total_price) three 1.user_id
    #  - 음식 수량(orders.total_qty) three 1.user_id
    #  - 결제 종류(default = Credit Card)(orders.payment) three 1.user_id
    #  - 상태 (버튼 클릭시 상태 변경)(order_detail.state) four 3.order_id
    #  - 요청 사항(orders.requests) three 1.user_id
    db = pymysql.connect(**config)
    cur = db.cursor()
    data_list_two = ()
    data_list_four = ()
    data_list_three = ()

    for i in user_no_list:
        sql = '''SELECT A.user_name,A.phone_number,B.store_id,B.order_id,B.order_time,B.total_price,B.total_qty,B.payment,B.requests 
        from users A INNER JOIN orders B
        ON A.user_no=B.user_no
        where B.user_no=%s
        '''
        cur.execute(sql, [data[0]])
        data_list_two += cur.fetchall()  #1~4

    for i in data_list_two:
        sql = "SELECT menu_name from menu where store_id=%s"
        cur.execute(sql, i[2])
        data_list_three += cur.fetchall()

    for i in data_list_two:
        sql = "SELECT order_state,order_id from orders where order_id=%s"
        cur.execute(sql, i[3])
        data_list_four += cur.fetchall()  #2~5

    data_list = []
    for i, j, k in zip(data_list_two, data_list_three, data_list_four):
        data_list.append(i + j + k)

    return render_template('jyj_order_detail.html', data_list=data_list)


@blueprint.route('/jyj_seller')
@requires_auth
def jyj_seller():

    #  - 구매자 이름(users.user_name) one
    #  - 구매자 연락처(users.phone_number) one
    #  - 음식 이름(menu.menu_name)  two 3.store_id
    #  - 주문 시간(orders.order_time) three 1.user_id
    #  - 총 가격(orders.total_price) three 1.user_id
    #  - 음식 수량(orders.total_qty) three 1.user_id
    #  - 결제 종류(default = Credit Card)(orders.payment) three 1.user_id
    #  - 상태 (버튼 클릭시 상태 변경)(order_detail.state) four 3.order_id
    #  - 요청 사항(orders.requests) three 1.user_id
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
@requires_auth
def store_save():
    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = "SELECT festival_name from festival"
    cur.execute(sql)

    data_list = cur.fetchall()
    return render_template('jyj_seller_apply.html', data_list=data_list)


@blueprint.route('/myajax_store_insert', methods=['POST'])
@requires_auth
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


@blueprint.route('/myajax_store_delete', methods=['POST'])
@requires_auth
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


@blueprint.route('/myajax_state_update', methods=['POST'])
@requires_auth
def myajax_state_update():

    json_data = request.get_json()
    # print(json_data)
    db = pymysql.connect(**config)

    data_list_one = {}
    cur = db.cursor()
    sql = "SELECT order_state from orders"
    cur.execute(sql)
    data_list_one = cur.fetchall()
    for i in data_list_one:
        if (i == '주문중', ):
            print("주문완료")
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