"""
Copyright (c) 2019 - present AppSeed.us
"""

from app.home import blueprint
from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
import flask_restful
import pymysql


config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'mysql',
    'database': 'mydb',
    'charset': 'utf8'
}

# <<<------------재성-------------->>>
@blueprint.route('/jaesung_festivalList')
def index():

    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = "SELECT * from festival"
    cur.execute(sql)

    data_list = cur.fetchall()
    
    return render_template('jaesung_festivalList.html', segment='index', data_list=data_list)


# <<<------------연옥-------------->>>
@blueprint.route('/jan_festival_using')
def index2():

    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = "SELECT * from festival, organization"
    cur.execute(sql)

    data_list = cur.fetchall()
    
    return render_template('jan_festival_using.html', segment='index2', data_list=data_list)


@blueprint.route('/jan_apply', methods=['GET', 'POST'])

def index2_1():
    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = "SELECT * from organization, festival"
    cur.execute(sql)

    data_list = cur.fetchall()
    
    return render_template('jan_apply.html', segment='index2_1', data_list=data_list)


@blueprint.route('/jan_festival', methods=['GET', 'POST'])
def index2_2():

    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = "SELECT * from festival"
    cur.execute(sql)

    data_list = cur.fetchall()
    
    return render_template('jan_festival.html', segment='index2_2', data_list=data_list)


# <<<------------현주_1-------------->>>

@blueprint.route('/juthor_dash')
@login_required
def index3():

    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = "SELECT * from festival"
    cur.execute(sql)

    data_list = cur.fetchall()
    
    return render_template('juthor_dash.html', segment='index3', data_list=data_list)


@blueprint.route('/juthor_category')
@login_required
def category():
    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = '''select unique category, count(category) as '가게 수'
             from store
             group by category'''
    cur.execute(sql)

    data_list = cur.fetchall()
    return render_template('juthor_category.html', segment='category', data_list=data_list)


@blueprint.route('/juthor_storelist')
@login_required
def store_list():
    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = '''select store_name, store_description, location_number
             from store
             where category="치킨"'''
    cur.execute(sql)

    data_list = cur.fetchall()
    return render_template('juthor_storeList.html', segment='storelist', data_list=data_list)


@blueprint.route('/juthor_storemenulist')
@login_required
def store_menulist():
    data_list = get_menu()
    return render_template('juthor_storemenulist.html', segment='storemenulist', data_list=data_list)


def get_menu():
    db = pymysql.connect(**config)

    cur = db.cursor()
    sql = '''select menu_name, menu_price from menu where store_id=3'''

    cur.execute(sql)
    data_list = cur.fetchall()

    return data_list


# <<<------------현재-------------->>>
@blueprint.route('/jhj_order')
@login_required
def order_get():
    conn = pymysql.connect(**config)
    cursor = conn.cursor()

    sql = '''SELECT total_price FROM orders WHERE order_id=2'''

    cursor.execute(sql)

    data_list = cursor.fetchall()

    return render_template('jhj_order.html', data_list=data_list)


@blueprint.route('/order_post', methods=['POST'])
@login_required
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


@blueprint.route('/jhj_credit')
@login_required
def credit_get():
    conn = pymysql.connect(**config)

    try:
        with conn.cursor() as cursor:
            sql = '''SELECT b.store_name, b.location_number FROM orders a LEFT JOIN store b 
                        ON a.store_id = b.store_id WHERE a.order_id = 2'''
            cursor.execute(sql)

        store_data = cursor.fetchall()

        with conn.cursor() as cursor:
            sql = "SELECT total_price FROM orders WHERE order_id=2"
            cursor.execute(sql)

        price_data = cursor.fetchall()

    finally:
        conn.close()

    return render_template('jhj_credit.html', data_store=store_data, data_price=price_data)



# <<<------------현주_2-------------->>>
@blueprint.route('/insert', methods=['POST'])
@login_required
def insert():
    data = request.get_json()

    print(type(data))
    print(data, "asdf")
    print("request: ", request.get_json())

# data 에서 받은 값들이 문자열로 내가 하나하나 다룰수있음을 확신하는 코드로 확인

# DB algo
    db = pymysql.connect(**config)
    cur = db.cursor()

    for d in data['menu']:
        sql = "insert into order_detail (order_id, menu_name, food_qty, food_price)\
               select 1, %s, 1, menu_price from menu where menu.menu_name=%s"
        cur.execute(sql, (d, d))

    db.commit()
    db.close()
    # return "hello"
    return render_template('juthor_cart.html', segment='cartlist')


@blueprint.route('/juthor_cart')
@login_required
def store_cartlist():
    data_list=get_cartlist()
    return render_template('juthor_cart.html', segment='cartlist', data_list=data_list)


def get_cartlist():
    db = pymysql.connect(**config)

    cur = db.cursor()
    sql = '''select menu_name, food_price, food_qty from order_detail where order_id=1'''

    cur.execute(sql)
    data_list = cur.fetchall()
    return data_list

  
@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith( '.html' ):
            template += '.html'

        # Detect the current page
        segment = get_segment( request )

        # Serve the file (if exists) from app/templates/FILE.html
        return render_template( template, segment=segment )

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