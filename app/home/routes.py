# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from app.home import blueprint
from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app import login_manager
from jinja2 import TemplateNotFound
import pymysql

config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'root0127:)',
    'database': 'mydb',
    'charset': 'utf-8'
}

@blueprint.route('/jan_festival_using')
@login_required
def index2():

    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = "SELECT * from festival, organization"
    cur.execute(sql)

    data_list = cur.fetchall()
    
    return render_template('jan_festival_using.html', segment='index2', data_list=data_list)

@blueprint.route('/jan_apply', methods=['GET', 'POST'])
@login_required
def index2_1():
    # if method == 


    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = "SELECT * from organization, festival"
    cur.execute(sql)

    data_list = cur.fetchall()
    
    return render_template('jan_apply.html', segment='index2_1', data_list=data_list)

@blueprint.route('/jan_festival', methods=['GET', 'POST'])
@login_required
def index2_2():

    db = pymysql.connect(**config)
    cur = db.cursor()
    sql = "SELECT * from festival"
    cur.execute(sql)

    data_list = cur.fetchall()
    
    return render_template('jan_festival.html', segment='index2_2', data_list=data_list)


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
