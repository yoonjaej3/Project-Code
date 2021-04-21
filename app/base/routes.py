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

# app2 = Flask(__name__, static_url_path='/static', static_folder='./static')
blueprint.config={}
blueprint.config['SECRET_KEY'] = constants.SECRET_KEY
blueprint.config['DEBUG'] = True


# app2 -> blueprint
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
            return redirect('/login')
        return f(*args, **kwargs)

    return decorated


config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
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
# app2 -> blueprint
@blueprint.route('/login_user')
def user_login():
    return render_template('accounts/home.html')

# app2 -> blueprint
@blueprint.route('/login_auth')
def auth_login():
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=AUTH0_AUDIENCE)

# app2 -> blueprint
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


# app2 -> blueprint
@blueprint.route('/dashboard')
@requires_auth
def dashboard():
    return render_template('accounts/dashboard.html',
                           userinfo=session[constants.PROFILE_KEY],
                           userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    login_form = LoginForm(request.form)
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        # ID            = request.form['ID']
        username      = request.form['username']
        email         = request.form['email']
        # Password      = request.form['Password']
        # User_catecory = request.form['User_category']
        # Phone_number  = request.form['Phone_number']
    

        # Check usename exists
        user = User.query.filter_by(username=username).first()
        
        # Check username exists
        # db = pymysql.connect(**config)
        # cur = db.cursor()
        # cur.execute('SELECT * FROM users WHERE ID = %s', (Username,))
        # user = cur.fetchone()
        if user:
            return render_template( 'accounts/register.html', 
                                    msg='Username already registered',
                                    success=False,
                                    form=create_account_form)

        # else we can create the user
        # cur.execute('INSERT INTO users VALUES (%s, %s, %s, %s, %s)', (ID, Username, Password, User_catecory, Phone_number,)) 
        # db.commit()
        
        # Check email exists
        user = User(**request.form)
        # sqlalchemy db
        db.session.add(user)
        db.session.commit()
        


        return render_template( 'accounts/register.html', 
                                msg='User created please <a href="/login">login</a>', 
                                success=True,
                                form=create_account_form)

    else:
        return render_template( 'accounts/register.html', form=create_account_form)


# app2 -> blueprint
@blueprint.route('/logout_auth')
def auth_logout():
    session.clear()
    return redirect(url_for('base_blueprint.index_init'))


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
