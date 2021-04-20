# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField
from wtforms.validators import InputRequired, Email, DataRequired

## login and registration

class LoginForm(FlaskForm):
    username = TextField    ('Username', id='username_login'   , validators=[DataRequired()])
    password = PasswordField('Password', id='pwd_login'        , validators=[DataRequired()])

class CreateAccountForm(FlaskForm):
    username = TextField('Username'     , id='username_create' , validators=[DataRequired()])
    email    = TextField('Email'        , id='email_create'    , validators=[DataRequired(), Email()])
    password = PasswordField('Password' , id='pwd_create'      , validators=[DataRequired()])
<<<<<<< HEAD

# 주최자등록폼
class RegisterOrganizationForm(FlaskForm):
    company_name = TextField('Organization'     , id='company_name' , validators=[DataRequired(), InputRequired()])
    manager_name = TextField('Manager'          , id='manager_name', validators=[DataRequired(), InputRequired()])
    manager_contact = TextField('Contact'    , id='manager_contact', validators = [InputRequired()])
=======
>>>>>>> 69574c152d43a8fab8837c63e50a56849886df94
