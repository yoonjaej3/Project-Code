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
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'mysql',
    'database': 'mydb',
    'charset': 'utf8'
}


@blueprint.route('/')
def route_default():
    return redirect(url_for('base_blueprint.index_init'))


@blueprint.route('/festival_init', methods=['GET', 'POST'])
def index_init():
    db = pymysql.connect(**config)
    cur = db.cursor()
    json_data = request.get_json()
    if json_data:
        sql = '''INSERT INTO festival(org_id, festival_name, period, location, url)
                VALUES(%s, %s, %s, %s, %s)'''
        cur.execute(sql, [json_data['org_id'], json_data['festival_name'],
                          json_data['period'], json_data['location'], json_data['url']])
        db.commit()

    sql = "SELECT * from festival"
    cur.execute(sql)

    data_list = cur.fetchall()
    
    return render_template('accounts/festival_init.html', segment='index_init', data_list=data_list)

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

    # insert user_category
    session[constants.JWT_PAYLOAD]['user_category'] = '관리자'
    
    db = pymysql.connect(**config)
    cur = db.cursor()
    cur.execute('SELECT * FROM users WHERE email = %s', [session[constants.JWT_PAYLOAD]['email']])
    check = cur.fetchone()
    
    # data insert
    if not check:
        sql = '''INSERT INTO users (user_category, email, user_name, phone_number) VALUES ('관리자', %s, %s, '')'''
        cur.execute(sql, [session[constants.JWT_PAYLOAD]['email'],session[constants.JWT_PAYLOAD]['name']])
        db.commit()
        is_admin = True
    else:
        is_admin = False

    # insert user_no
    cur.execute('SELECT user_no FROM users WHERE email = %s', [session[constants.JWT_PAYLOAD]['email']])
    user_num = cur.fetchone()
    session[constants.JWT_PAYLOAD]['user_no'] = user_num[0]

    return render_template('accounts/register_admin.html', is_admin=is_admin, userinfo=session[constants.PROFILE_KEY])
    

# organizer register
@blueprint.route('/register_org')
@requires_auth
def org_register():

    # insert user_category
    session[constants.JWT_PAYLOAD]['user_category'] = '주최자'

    db = pymysql.connect(**config)
    cur = db.cursor()
    cur.execute('SELECT * FROM users WHERE email = %s', [session[constants.JWT_PAYLOAD]['email']])
    check = cur.fetchone()
    
    if not check:
        sql = '''INSERT INTO users (user_category, email, user_name, phone_number) VALUES ('주최자', %s, %s, '')'''
        cur.execute(sql, [session[constants.JWT_PAYLOAD]['email'],session[constants.JWT_PAYLOAD]['name']])
        db.commit()
        is_org = True
    else:
        is_org = False

    # insert user_no
    cur.execute('SELECT user_no FROM users WHERE email = %s', [session[constants.JWT_PAYLOAD]['email']])
    user_num = cur.fetchone()
    session[constants.JWT_PAYLOAD]['user_no'] = user_num[0]

    return render_template('accounts/register_org.html', is_org=is_org, userinfo=session[constants.PROFILE_KEY])


# seller register
@blueprint.route('/register_seller')
@requires_auth
def seller_register():

    # insert user_category
    session[constants.JWT_PAYLOAD]['user_category'] = '판매자'

    db = pymysql.connect(**config)
    cur = db.cursor()
    cur.execute('SELECT * FROM users WHERE email = %s', [session[constants.JWT_PAYLOAD]['email']])
    check = cur.fetchone()
    
    if not check:
        sql = '''INSERT INTO users (user_category, email, user_name, phone_number) VALUES ('판매자', %s, %s, '')'''
        cur.execute(sql, [session[constants.JWT_PAYLOAD]['email'],session[constants.JWT_PAYLOAD]['name']])
        db.commit()
        is_seller = True
    else:
        is_seller = False
    
    # insert user_no
    cur.execute('SELECT user_no FROM users WHERE email = %s', [session[constants.JWT_PAYLOAD]['email']])
    user_num = cur.fetchone()
    session[constants.JWT_PAYLOAD]['user_no'] = user_num[0]

    return render_template('accounts/register_seller.html', is_seller=is_seller, userinfo=session[constants.PROFILE_KEY])


# buyer register
@blueprint.route('/register_buyer')
@requires_auth
def buyer_register():
    
    # insert user_category
    session[constants.JWT_PAYLOAD]['user_category'] = '구매자'

    db = pymysql.connect(**config)
    cur = db.cursor()
    cur.execute('SELECT * FROM users WHERE email = %s', [session[constants.JWT_PAYLOAD]['email']])
    check = cur.fetchone()
    
    if not check:
        sql = '''INSERT INTO users (user_category, email, user_name, phone_number) VALUES ('구매자', %s, %s, '')'''
        cur.execute(sql, [session[constants.JWT_PAYLOAD]['email'],session[constants.JWT_PAYLOAD]['name']])
        db.commit()
        is_buyer = True
    else:
        is_buyer = False
    
    # insert user_no
    cur.execute('SELECT user_no FROM users WHERE email = %s', [session[constants.JWT_PAYLOAD]['email']])
    user_num = cur.fetchone()
    session[constants.JWT_PAYLOAD]['user_no'] = user_num[0]

    return render_template('accounts/register_buyer.html', is_buyer=is_buyer, userinfo=session[constants.PROFILE_KEY])


@blueprint.route('/old_user')
@requires_auth
def old_user():

    db = pymysql.connect(**config)
    cur = db.cursor()
    cur.execute('SELECT * FROM users WHERE email = %s', [session[constants.JWT_PAYLOAD]['email']])
    check = cur.fetchone()

    # 계정이 없는 경우 dashboard로 되돌아감
    if not check:
        is_user = False
        return render_template('accounts/dashboard.html', is_user=is_user)
    
    # 계정이 있으므로 insert user_no and user_category
    cur.execute('SELECT user_no, user_category FROM users WHERE email = %s', [session[constants.JWT_PAYLOAD]['email']])
    user_num = cur.fetchone()
    print('============================')
    print(user_num)
    print('============================')
    
    session[constants.JWT_PAYLOAD]['user_no'] = user_num[0]
    session[constants.JWT_PAYLOAD]['user_category'] = user_num[1]
    print('============================')
    print(session)
    print('============================')
    
    return redirect(url_for('home_blueprint.index'))
    

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
