# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import jsonify, render_template, redirect, request, url_for
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

@blueprint.route('/')
def route_default():
    return redirect(url_for('base_blueprint.login'))

## Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:
        
        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = User.query.filter_by(username=username).first()
        
        # Check the password
        if user and verify_pass( password, user.password):

            login_user(user)
            return redirect(url_for('base_blueprint.route_default'))

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
    cur.execute('SELECT * FROM users WHERE email = %s', [session[constants.JWT_PAYLOAD]['email']])
    check = cur.fetchone()
    
    if not check:
        sql = '''INSERT INTO users (user_category, email, user_name, phone_number) VALUES ('관리자', %s, %s, '')'''
        cur.execute(sql, [session[constants.JWT_PAYLOAD]['email'],session[constants.JWT_PAYLOAD]['name']])
        db.commit()
        is_admin = True
    else:
        is_admin = False

    if not current_user.is_authenticated:
        return render_template( 'accounts/login.html',
                                form=login_form)
    return redirect(url_for('home_blueprint.index'))

    return render_template('accounts/register_admin.html', is_admin=is_admin, userinfo=session[constants.PROFILE_KEY])
    

# organizer register
@blueprint.route('/register_org')
@requires_auth
def org_register():
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

    return render_template('accounts/register_org.html', is_org=is_org, userinfo=session[constants.PROFILE_KEY])


# seller register
@blueprint.route('/register_seller')
@requires_auth
def seller_register():
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

    return render_template('accounts/register_seller.html', is_seller=is_seller, userinfo=session[constants.PROFILE_KEY])


# buyer register
@blueprint.route('/register_buyer')
@requires_auth
def buyer_register():
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

    return render_template('accounts/register_buyer.html', is_buyer=is_buyer, userinfo=session[constants.PROFILE_KEY])

@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('base_blueprint.login'))


# ## ------- 주최자 등록  ------------
# @blueprint.route('/org/register', methods='GET', 'POST')
# def register_org():
#     # login_form = LoginForm(request.form)
#     org_register = RegisterOrganizationForm(request.form)
#     if '' in request.form:
#         username  = request.form['username']
#         email     = request.form['email'   ]

#         # Check usename exists
#         user = User.query.filter_by(username=username).first()
#         if user:
#             return render_template( 'accounts/register.html', 
#                                     msg='Username already registered',
#                                     success=False,
#                                     form=create_account_form)

#         # Check email exists
#         user = User.query.filter_by(email=email).first()
#         if user:
#             return render_template( 'accounts/register.html', 
#                                     msg='Email already registered', 
#                                     success=False,
#                                     form=create_account_form)
    

    

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


