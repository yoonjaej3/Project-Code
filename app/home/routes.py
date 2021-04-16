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

@blueprint.route('/store_save')
@login_required
def store_save():
    return render_template('store_save.html')

@blueprint.route('/myajax',methods=['POST'])
@login_required
def myajax():

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
    # db = pymysql.connect(host="localhost", user="root", password="1234",
    #                     db="mydb", charset="utf8")
    # cur = db.cursor()
    #  json_data = request.get_json()
    #     json_data['store_id'] = store_id
    #     json_data['created__at'] = str(datetime.today())

    #     # DB insert
    #     sql = '''Insert into store(store_id,festival_id,store_name,store_description ,contact_number,category,license_number,location_number,created_at) 
    #      values(?,?,?,?,?,?,?,?,?);
    #     '''
    #     #    Insert into store(store_id,festival_id,store_name,store_description ,contact_number,category,license_number,location_number,created_at)
    #     #    values(1,1,"떡꼬치 가게","달콤하고 매운 떡꼬치를 파는 곳입니다.","010-9062-6317","꼬치","A123","A-3","2000-01-11 00:00:00");

    #     self.cursor.execute(sql, [
    #         json_data['store_id'], json_data['festival_id'],
    #         json_data['store_name'], json_data['store_description'],
    #         json_data['contact_number'], json_data['category'],
    #         json_data['license_number'], json_data['location_number'],
    #         json_data['created__at']
    #     ])

    #     self.conn.commit()    
    # sql = "SELECT * from store"
    # cur.execute(sql)

    # data_list = cur.fetchall()
    
    # return render_template('store_save.html',data_list=data_list)


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
