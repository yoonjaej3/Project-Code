# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from app.home import blueprint
from flask import render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
import flask_restful
from app import login_manager
from jinja2 import TemplateNotFound
import pymysql


config = {
    'host': '127.0.0.1',
    'port': 13306,
    'user': 'root',
    'database': 'mydb'
}


@blueprint.route('/jaesung_festivalList')
@login_required
def index():

    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = "SELECT * from festival"
    cur.execute(sql)

    data_list = cur.fetchall()
    
    return render_template('jaesung_festivalList.html', segment='index', data_list=data_list)


@blueprint.route('/jan_festival')
@login_required
def index2():

    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = "SELECT * from festival"
    cur.execute(sql)

    data_list = cur.fetchall()
    
    return render_template('jan_festival.html', segment='index2', data_list=data_list)


@blueprint.route('/juthor_dash')
@login_required
def index3():

    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = "SELECT * from festival"
    cur.execute(sql)

    data_list = cur.fetchall()
    
    return render_template('juthor_dash.html', segment='index3', data_list=data_list)


class Order(flask_restful.Resource):
    def __init__(self):
        self.conn = pymysql.connect(**config)
        self.cursor = self.conn.cursor()

    @blueprint.route('/jhj_order')
    @login_required
    def order_get(self, order_id):
        sql = '''SELECT total_price FROM orders WHERE order_id=2'''

        self.cursor.execute(sql)

        data_list = self.cursor.fetchall()

        return render_template('jhj_order.html', data_list=data_list)

    @blueprint.route('/order_post', methods=['POST'])
    @login_required
    def order_post(self):
        json_data = request.get_json()

        try:
            with self.conn.cursor() as cursor:
                sql = "UPDATE users SET phone_number=%s WHERE user_id=3"
                self.cursor.execute(sql, [json_data['phone_number']])

            self.conn.commit()

            with self.conn.cursor() as cursor:
                sql = "UPDATE orders SET requests=%s WHERE order_id=3"
                self.cursor.execute(sql, [json_data['request_text']])

            self.conn.commit()

        finally:
            self.conn.close()

        return jsonify(result="success", result2=json_data)

    @blueprint.route('/jhj_credit')
    @login_required
    def credit_get(self):
        try:
            with self.conn.cursor() as cursor:
                sql = '''SELECT b.store_name, b.location_number FROM orders a LEFT JOIN store b 
                        ON a.store_id = b.store_id WHERE a.order_id = 2'''
                self.cursor.execute(sql)

            store_data = self.cursor.fetchall()

            with self.conn.cursor() as cursor:
                sql = "SELECT total_price FROM orders WHERE order_id=2"
                self.cursor.execute(sql)

            price_data = self.cursor.fetchall()

        finally:
            self.conn.close()

        return render_template('jhj_credit.html', data_store=store_data, data_price=price_data)


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
