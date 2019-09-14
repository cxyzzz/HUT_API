import os

from flask import (flash, make_response, redirect, render_template,
                   request, send_from_directory, session, url_for)
# import json
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import InputRequired
import datetime
from app import app
from HUT import My_Calendar, Student


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
        print(datetime.datetime.now())
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
            print(session)
            return redirect(url_for('index'))
        return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def index():
    if session.get('data'):
        return render_template('index.html', **session['data'])
    if (session.get('account') and session.get('password')):
        account = session['account']
        password = session['password']
        test = Student(account, password)
        if test.HEADERS['token'] == '-1':
            error = '错误的账号或密码'
            return render_template('test.html', form=MyForm(), error=error)
        session['data'] = test.gen_Kb_web_data()
        print(datetime.datetime.now())
        return render_template('index.html', **session['data'])
    else:
        return redirect(url_for('login'))


@app.route('/gen_cal')
def gen_cal():
    print(datetime.datetime.now())
    if (request.args.get('xh') and request.args.get('pwd')):
        account = request.args.get('xh')
        password = request.args.get('pwd')
        filename = account + '.ics'
        t = My_Calendar(filename, account, password)
        if t.student.HEADERS['token'] == '-1':
            error = '错误的账号或密码'
            return render_template('test.html', form=MyForm(), error=error)
        t.gen_cal()
        directory = os.getcwd()
        response = make_response(send_from_directory(
            directory, filename, as_attachment=True))
        print(datetime.datetime.now())
        return response

    try:
        account = session['account']
        password = session['password']
        print(session)
        filename = account + '.ics'
        t = My_Calendar(filename, account, password)
        t.gen_cal()
        directory = os.getcwd()
        response = make_response(send_from_directory(
            directory, filename, as_attachment=True))
        print(datetime.datetime.now())
        return response
    except KeyError:
        return redirect(url_for('login'))


@app.route('/signout')
def signout():
    session.clear()
    return redirect(url_for('login'))
