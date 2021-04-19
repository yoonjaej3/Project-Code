# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from app.home import blueprint
from flask import render_template, redirect, url_for, request,jsonify
from flask_login import login_required, current_user
from app import login_manager
from jinja2 import TemplateNotFound
import pymysql
from datetime import datetime
@blueprint.route('/index')
@login_required
def index():

    db = pymysql.connect(host="localhost", user="root", password="1234",
                        db="mydb", charset="utf8")
    cur = db.cursor()
    sql = "SELECT * from festival"
    cur.execute(sql)

    data_list = cur.fetchall()
    
    return render_template('index.html', segment='index', data_list=data_list)

@blueprint.route('/store_info')
@login_required
def store_info():

    db = pymysql.connect(host="localhost", user="root", password="1234",
                        db="mydb", charset="utf8")
    cur = db.cursor()
    sql = "SELECT * from store"
    cur.execute(sql)

    data_list = cur.fetchall()
    
    return render_template('store_info.html',data_list=data_list)

@blueprint.route('/order_detail')
@login_required
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
    db = pymysql.connect(host="localhost", user="root", password="1234",
                        db="mydb", charset="utf8")
    cur = db.cursor()

    
    data_list_two=() 
    data_list_four=()
    data_list_three=()
    user_id_list=[]
    sql = "SELECT user_id,user_name,phone_number from users"
    cur.execute(sql)
    data_list_one = cur.fetchall()
    
    for i in data_list_one:
        user_id_list.append(i[0])

    for i in user_id_list:
        sql = '''SELECT A.user_name,A.phone_number,B.store_id,B.order_id,B.order_time,B.total_price,B.total_qty,B.payment,B.requests 
        from users A INNER JOIN orders B
        ON A.user_id=B.user_id
        where B.user_id=%s
        '''
        cur.execute(sql,i)
        data_list_two+= cur.fetchall()   #1~4

    for i in data_list_two:
        sql = "SELECT menu_name from menu where store_id=%s"
        cur.execute(sql,i[2])
        data_list_three+= cur.fetchall() 

    for i in data_list_two:
        sql = "SELECT order_state from order_detail where order_id=%s"
        cur.execute(sql,i[3])
        data_list_four+= cur.fetchall()   #2~5

   
    
    data_list=[]
    for i,j,k in zip(data_list_two,data_list_three,data_list_four):
        data_list.append(i+j+k);
   
    print(data_list)
    return render_template('order_detail.html',data_list=data_list)

@blueprint.route('/store_save')
@login_required
def store_save():
    return render_template('store_save.html')

@blueprint.route('/myajax_store_insert',methods=['POST'])
@login_required
def myajax_store_insert():

    json_data = request.get_json()
    db = pymysql.connect(host="localhost", user="root", password="1234",
                        db="mydb", charset="utf8")
    cur = db.cursor()


    sql = '''Insert into store(festival_id,store_name,store_description ,contact_number,category,license_number,location_number,created_at) 
    values(%s,%s,%s,%s,%s,%s,%s,%s);
    '''
   
    json_data['created__at'] = str(datetime.today())
    cur.execute(sql, [
            json_data['festival_id'],
            json_data['store_name'], json_data['store_description'],
            json_data['contact_number'], json_data['category'],
            json_data['license_number'], json_data['location_number'],
            json_data['created__at']
    ])
   
    db.commit() 

    return jsonify(result = "success", result2= json_data)
  
@blueprint.route('/myajax_store_delete',methods=['POST'])
@login_required
def myajax_store_delete():

    json_data = request.get_json()
    print(json_data)
    db = pymysql.connect(host="localhost", user="root", password="1234",
                        db="mydb", charset="utf8")
    cur = db.cursor()


    sql = '''Delete from store where store_id=%s
    '''
    cur.execute(sql, [json_data['store_id']])
   
    db.commit()   

    return jsonify(result = "success", result2= json_data)



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
def get_segment( request ): 

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment    

    except:
        return None  
