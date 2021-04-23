# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from app.base import constants
from app.base.routes import requires_auth, session
from app.home import blueprint
from flask import render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app import login_manager
from jinja2 import TemplateNotFound
import pymysql
import json
from datetime import datetime

config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password':'mysql',
    'database': 'mydb',
    'charset': 'utf8'
}


@blueprint.route('/jaesung_festivalList')
@requires_auth
def index():

    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = "SELECT * from festival"
    cur.execute(sql)

    data_list = cur.fetchall()

    # sql2 = "SELECT * from users"
    # cur.execute(sql2)
    user_data = session[constants.JWT_PAYLOAD]['name']

    print(user_data)
    return render_template('jaesung_festivalList.html',
                           segment='index',
                           data_list=data_list,
                           user_data=user_data)


# <<<------------연옥-------------->>>
@blueprint.route('/admin_index')

def index2():

    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = "SELECT * from festival"
    cur.execute(sql)

    data_list = cur.fetchall()

    return render_template('jan_festival.html',
                           segment='index2',
                           data_list=data_list)


@blueprint.route('/jan_apply/', methods=['GET', 'POST'])
def index2_1_1():
    db = pymysql.connect(**config)
    c = db.cursor()

    sql = "SELECT * FROM festival LEFT OUTER JOIN users ON festival.user_no=users.user_no where users.user_no = 3"
    c.execute(sql)
    
    data_list = c.fetchall()
    
    return jsonify(result="success", result2=data_list)


@blueprint.route('/jan_festival')
def index2_2():

    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = "SELECT * from festival"
    cur.execute(sql)

    data_list = cur.fetchall()
    
    return render_template('jan_festival.html', segment='index2_2', data_list=data_list)


# <<<------------현주_1-------------->>>

@blueprint.route('/juthor_dash')
def index3():

    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = "SELECT * from festival"
    cur.execute(sql)

    data_list = cur.fetchall()

    return render_template('juthor_dash.html',
                           segment='index3',
                           data_list=data_list)


@blueprint.route('/jhj_order')
def order():
    conn = pymysql.connect(**config)
    cursor = conn.cursor()

    sql = '''SELECT total_price FROM orders WHERE order_id=3'''

    cursor.execute(sql)

    data_list = cursor.fetchall()

    return render_template('jhj_order.html', data_list=data_list)


@blueprint.route('/order_post', methods=['POST'])
def order_post():
    json_data = request.get_json()

    conn = pymysql.connect(**config)

    try:
        with conn.cursor() as cursor:
            sql = "UPDATE users SET phone_number=%s WHERE user_id=3"
            cursor.execute(sql, [json_data['phone_number']])

        conn.commit()

        with conn.cursor() as cursor:
            sql = "UPDATE orders SET requests=%s WHERE order_id=3"
            cursor.execute(sql, [json_data['request_text']])

        conn.commit()

    finally:
        conn.close()

    return jsonify(result="success", result2=json_data)


# @blueprint.route('/jhj_credit', methods=['POST'])
# @login_required
# def credit_get():


@blueprint.route('/jyj_seller_info')
def store_info():

    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = "SELECT * from store"
    cur.execute(sql)

    data_list = cur.fetchall()

    return render_template('jyj_seller_info.html', data_list=data_list)


@blueprint.route('/jyj_order_detail')
def order_detail():

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
    data_list_one = ()
    data_list_two = ()
    data_list_four = ()
    data_list_three = ()
    user_no_list = []
    sql = "SELECT user_no,user_id,user_name,phone_number from users"
    cur.execute(sql)
    data_list_one = cur.fetchall()

    for i in data_list_one:
        user_no_list.append(i[0])

    for i in user_no_list:
        sql = '''SELECT A.user_name,A.phone_number,B.store_id,B.order_id,B.order_time,B.total_price,B.total_qty,B.payment,B.requests 
        from users A INNER JOIN orders B
        ON A.user_no=B.user_no
        where B.user_no=%s
        '''
        cur.execute(sql, i)
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
def store_save():
    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = "SELECT festival_name from festival"
    cur.execute(sql)

    data_list = cur.fetchall()
    return render_template('jyj_seller_apply.html', data_list=data_list)


@blueprint.route('/myajax_store_insert', methods=['POST'])
def myajax():

    json_data = request.get_json()
    db = pymysql.connect(host="localhost",
                         user="root",
                         password="1234",
                         db="mydb",
                         charset="utf8")
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
    # cur.execute(sql, [json_data['order_state']])
    # if(json_data['order_state']=='주문중')
    #     json_data['order_state']=="주문완료"
    # sql = '''Update orders SET order_state=%s
    # '''
    # cur.execute(sql, [json_data['order_state']])

    # print(json_data['order_id'])
    # db.commit()

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
