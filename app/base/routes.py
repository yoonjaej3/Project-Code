# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import jsonify, render_template, redirect, request, url_for, session
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)

from app import db, login_manager
from app.base import blueprint
from app.base.forms import LoginForm, CreateAccountForm
from app.base.models import User

from app.base.util import verify_pass
import pymysql, json

from flask import Flask
from authlib.integrations.flask_client import OAuth
from functools import wraps
from os import environ as env
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv, find_dotenv
from six.moves.urllib.parse import urlencode
from kafka import KafkaProducer

from app.base import constants

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AUTH0_CALLBACK_URL = env.get(constants.AUTH0_CALLBACK_URL)
AUTH0_CLIENT_ID = env.get(constants.AUTH0_CLIENT_ID)
AUTH0_CLIENT_SECRET = env.get(constants.AUTH0_CLIENT_SECRET)
AUTH0_DOMAIN = env.get(constants.AUTH0_DOMAIN)
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
AUTH0_AUDIENCE = env.get(constants.AUTH0_AUDIENCE)

blueprint.config={}
blueprint.config['SECRET_KEY'] = constants.SECRET_KEY
blueprint.config['DEBUG'] = True

# Kafka Producer
producer = KafkaProducer(acks='all', client_id='last_modify', bootstrap_servers=["172.20.0.101:9092"])


@blueprint.errorhandler(Exception)
def handle_auth_error(ex):
    response = jsonify(message=str(ex))
    response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
    return response


oauth = OAuth(blueprint)

auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    access_token_url=AUTH0_BASE_URL + '/oauth/token',
    authorize_url=AUTH0_BASE_URL + '/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if constants.PROFILE_KEY not in session:
            return redirect('/login_user')
        return f(*args, **kwargs)
    
    return decorated


config = {
    'host': '172.20.0.2',
    'port': 3306,
    'user': 'root',
    'database': 'mydb',
    'charset': 'utf8'
}

def get_id():
    conn = pymysql.connect(**config)
    cur = conn.cursor()

    sql = "SELECT user_no FROM users WHERE email = %s"

    cur.execute(sql, [session[constants.JWT_PAYLOAD]['email']])

    user_no = cur.fetchone()

    return user_no


@blueprint.route('/')
def route_default():
    return redirect(url_for('base_blueprint.index_init'))


@blueprint.route('/index', methods=['GET', 'POST'])
def index_init():
    db = pymysql.connect(**config)
    cur = db.cursor()

    sql = "SELECT * from festival"
    cur.execute(sql)

    data_list = cur.fetchall()

    return render_template('accounts/index.html', segment='index_init', data_list=data_list)


## Login & Registration
@blueprint.route('/login_user')
def user_login():
    return render_template('accounts/home.html')


@blueprint.route('/login_auth')
def auth_login():
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=AUTH0_AUDIENCE)


@blueprint.route('/callback')
def callback_handling():
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()
    
    session[constants.JWT_PAYLOAD] = userinfo
    session[constants.PROFILE_KEY] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return redirect('/dashboard')


@blueprint.route('/dashboard')
@requires_auth
def dashboard():
    userinfo_pretty = json.dumps(session[constants.JWT_PAYLOAD], indent=4, ensure_ascii=False)
    
    return render_template('accounts/dashboard.html',
                           userinfo=session[constants.PROFILE_KEY],
                           userinfo_pretty=userinfo_pretty)


# admin register
@blueprint.route('/register_admin')
@requires_auth
def admin_register():   
    db = pymysql.connect(**config)
    cur = db.cursor()
    sql_s = 'SELECT * FROM users WHERE email = %s'
    data = cur.execute(sql_s, [session[constants.JWT_PAYLOAD]['email']])

    admin = 'admin'

    if int(data) == 0:
        sql = '''INSERT INTO users (user_category, email, user_name) VALUES (%s, %s, %s)'''
        cur.execute(sql, [admin, session[constants.JWT_PAYLOAD]['email'], session[constants.JWT_PAYLOAD]['name']])
 
        db.commit()
        
        # 현재 접속한 user_no
        user_no = get_id()
        # Kafka에 전송할 JSON data
        d = {
            'user_no' : user_no[0],
            'user_category' : admin,
            'email' : session[constants.JWT_PAYLOAD]['email'],
            'user_name' : session[constants.JWT_PAYLOAD]['name'],
            'phone_number' : None
        }

        producer.send('my_topic_users', value=json.dumps(d, ensure_ascii=False, default=str).encode())
        producer.flush()

        is_admin = True
    else:
        is_admin = False

    cur.execute(sql_s, [session[constants.JWT_PAYLOAD]['email']])
    
    check = cur.fetchone()
    user = check[1]

    return render_template('accounts/register_admin.html', user=user, is_admin=is_admin, userinfo=session[constants.PROFILE_KEY])
    

# organizer register
@blueprint.route('/register_org')
@requires_auth
def manager_register():
    db = pymysql.connect(**config)
    cur = db.cursor()
    sql_s = 'SELECT * FROM users WHERE email = %s'
    data = cur.execute(sql_s, [session[constants.JWT_PAYLOAD]['email']])

    manager = 'manager'

    if int(data) == 0:
        sql = '''INSERT INTO users (user_category, email, user_name) VALUES (%s, %s, %s)'''
        cur.execute(sql, [manager, session[constants.JWT_PAYLOAD]['email'], session[constants.JWT_PAYLOAD]['name']])
        db.commit()

        # 현재 접속한 user_no
        user_no = get_id()
        # Kafka에 전송할 JSON data
        d = {
            'user_no' : user_no[0],
            'user_category' : manager,
            'email' : session[constants.JWT_PAYLOAD]['email'],
            'user_name' : session[constants.JWT_PAYLOAD]['name'],
            'phone_number' : None
        }  
        
        producer.send('my_topic_users', value=json.dumps(d, ensure_ascii=False, default=str).encode())
        producer.flush()

        is_org = True
    else:
        is_org = False
    
    cur.execute(sql_s, [session[constants.JWT_PAYLOAD]['email']])
    
    check = cur.fetchone()
    user = check[1]

    return render_template('accounts/register_org.html', user=user, is_org=is_org, userinfo=session[constants.PROFILE_KEY])


# seller register
@blueprint.route('/register_seller')
@requires_auth
def seller_register():
    db = pymysql.connect(**config)
    cur = db.cursor()
    sql_s = 'SELECT * FROM users WHERE email = %s'
    data = cur.execute(sql_s, [session[constants.JWT_PAYLOAD]['email']])

    seller = 'seller'

    if int(data) == 0:
        sql = '''INSERT INTO users (user_category, email, user_name) VALUES (%s, %s, %s)'''
        cur.execute(sql, [seller, session[constants.JWT_PAYLOAD]['email'], session[constants.JWT_PAYLOAD]['name']])
        db.commit()

        # 현재 접속한 user_no
        user_no = get_id()
        # Kafka에 전송할 JSON data
        d = {
            'user_no' : user_no[0],
            'user_category' : seller,
            'email' : session[constants.JWT_PAYLOAD]['email'],
            'user_name' : session[constants.JWT_PAYLOAD]['name'],
            'phone_number' : None
        }  
        
        producer.send('my_topic_users', value=json.dumps(d, ensure_ascii=False, default=str).encode())
        producer.flush()

        is_seller = True
    else:
        is_seller = False

    cur.execute(sql_s, [session[constants.JWT_PAYLOAD]['email']])
    
    check = cur.fetchone()
    user = check[1]

    return render_template('accounts/register_seller.html', user=user, is_seller=is_seller, userinfo=session[constants.PROFILE_KEY])


# buyer register
@blueprint.route('/register_customer')
@requires_auth
def buyer_register():
    db = pymysql.connect(**config)
    cur = db.cursor()
    sql_s = 'SELECT * FROM users WHERE email = %s'
    data = cur.execute(sql_s, [session[constants.JWT_PAYLOAD]['email']])

    user = 'customer'

    if int(data) == 0:
        sql = '''INSERT INTO users (user_category, email, user_name) VALUES (%s, %s, %s)'''
        cur.execute(sql, [user, session[constants.JWT_PAYLOAD]['email'], session[constants.JWT_PAYLOAD]['name']])
        db.commit()

        # 현재 접속한 user_no
        user_no = get_id()
        # Kafka에 전송할 JSON data
        d = {
            'user_no' : user_no[0],
            'user_category' : user,
            'email' : session[constants.JWT_PAYLOAD]['email'],
            'user_name' : session[constants.JWT_PAYLOAD]['name'],
            'phone_number' : None
        }  
        
        producer.send('my_topic_users', value=json.dumps(d, ensure_ascii=False, default=str).encode())
        producer.flush()
      
        is_buyer = True
    else:
        is_buyer = False
    
    cur.execute(sql_s, [session[constants.JWT_PAYLOAD]['email']])
    
    check = cur.fetchone()
    user = check[1]

    return render_template('accounts/register_customer.html', user=user, is_buyer=is_buyer, userinfo=session[constants.PROFILE_KEY])


@blueprint.route('/logout_auth')
def auth_logout():
    session.clear()
    params = {'returnTo': url_for('base_blueprint.route_default', _external=True), 'client_id': AUTH0_CLIENT_ID}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


## Errors
@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('page-500.html'), 500