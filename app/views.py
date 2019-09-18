import os

from flask import (Blueprint, flash, make_response, redirect, render_template,
                   request, send_from_directory, session, url_for)
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import InputRequired
from app.HUT import Student, My_Calendar

hut = Blueprint('hut', __name__, template_folder='templates')

    
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


@hut.route('/login', methods=['GET', 'POST'])
def login():
    form = MyForm()

    if request.method == 'GET':
        return render_template('login.html', form=form, error=None)

    if request.method == 'POST':
        if form.validate_on_submit():
            account = request.form.get("account", type=str, default=None)
            password = request.form.get("password", type=str, default=None)
            test = Student(account, password)
            if test.HEADERS['token'] == '-1':
                flash('用户名或密码错误...', category='error')
                return render_template('login.html', form=form)

            session.permanent = True
            session['account'] = account
            session['password'] = password
            # print(session)
            return redirect(url_for('hut.index'))
        print('*'*50)
        return redirect(url_for('hut.login'))

           
@hut.route('/', methods=['GET', 'POST'])
def index():
    if session.get('data'):
        return render_template('index.html', **session['data'])
    if (session.get('account') and session.get('password')):
        account = session['account']
        password = session['password']
        test = Student(account, password)
        if test.HEADERS['token'] == '-1':
            flash('用户名或密码错误...', category='error')
            return render_template('login.html', form=MyForm())
        session['data'] = test.gen_Kb_web_data()
        return render_template('index.html', **session['data'])
    else:
        return redirect(url_for('hut.login'))


@hut.route('/gen_cal')
def gen_cal():
    if (request.args.get('xh') and request.args.get('pwd')):
        account = request.args.get('xh')
        password = request.args.get('pwd')
        filename = account + '.ics'
        t = My_Calendar(filename, account, password)
        if t.student.HEADERS['token'] == '-1':
            flash('用户名或密码错误...', category='error')
            return render_template('login.html', form=MyForm())
        t.gen_cal()
        directory = os.getcwd()
        response = make_response(send_from_directory(
            directory, filename, as_attachment=True))
        return response

    if (session['account']):
        account = session['account']
        password = session['password']
        filename = account + '.ics'
        t = My_Calendar(filename, account, password)
        t.gen_cal()
        directory = os.getcwd()
        response = make_response(send_from_directory(
            directory, filename, as_attachment=True))
        return response
    else:
        return redirect(url_for('hut.login'))

 
@hut.route('/signout')
def signout():
    session.clear()
    return redirect(url_for('hut.login'))
