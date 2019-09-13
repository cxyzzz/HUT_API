from flask import flash, redirect, render_template, session, url_for, request, send_file, send_from_directory, make_response
from app import app
# import json
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired
from HUT import Student, My_Calendar
import os


class MyForm(FlaskForm):
    account = StringField(
        label='学号',
        validators=[InputRequired(message=u'学号不能为空')]
    )
    password = PasswordField(
        label='密码',
        validators=[InputRequired(message=u'密码不能为空')]
    )
    submit = SubmitField('Go')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = MyForm()

    if request.method == 'GET':
        return render_template('test.html', form=form, error=None)

    if request.method == 'POST':
        if form.validate_on_submit():
            account = request.form.get("account", type=str, default=None)
            password = request.form.get("password", type=str, default=None)

            test = Student(account, password)

            if test.HEADERS['token'] == '-1':
                error = '错误的账号或密码'
                return render_template('test.html', form=form, error=error)

            session.permanent = True
            session['account'] = account
            session['password'] = password

            flash('You were successfully logged in')
            return redirect(url_for('index'))
        return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def index():
    if (session.get('account') and session.get('password')):
        account = session['account']
        password = session['password']
        test = Student(account, password)
        if test.HEADERS['token'] == '-1':
            error = '错误的账号或密码'
            return render_template('test.html', form=MyForm(), error=error)
        data = test.gen_Kb_web_data()
        flash('You were successfully logged in')
        return render_template('index.html', **data)

    else:
        if request.method == 'GET':
            return redirect(url_for('login'))


@app.route('/gen_cal')
def gen_cal():
    global account
    account = session['account']
    global password
    password = session['password']

    filename = account + '.ics'
    t = My_Calendar(filename)
    t.gen_cal()
    directory = os.getcwd()
    response = make_response(send_from_directory(
        directory, filename, as_attachment=True))
    return response
