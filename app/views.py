import os
import requests
import json
from flask import (Blueprint, flash, make_response, redirect, render_template,
                   request, send_from_directory, session, url_for)
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import InputRequired
from app.HUT import Student, CurriculumCalendar, ElectricityFeeInquiry, JobCalendar

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
            # print(request.form)
            account = request.form.get("account", type=str, default=None)
            password = request.form.get("password", type=str, default=None)
            student = Student(account, password)
            if student.HEADERS['token'] == '-1':
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
        print(session['data'])
        return render_template('index.html', **session['data'])
    if (session.get('account') and session.get('password')):
        account = session['account']
        password = session['password']
        student = Student(account, password)
        if student.HEADERS['token'] == '-1':
            flash('用户名或密码错误...', category='error')
            return render_template('login.html', form=MyForm())
        session['data'] = student.gen_Kb_json_data()
        data = student.gen_Kb_web_data(session['data'])
        return render_template('index.html', **data)
    else:
        return redirect(url_for('hut.login'))


@hut.route('/gen_cal')
def gen_cur_cal():
    if (request.args.get('xh') and request.args.get('pwd')):
        account = request.args.get('xh')
        password = request.args.get('pwd')
        filename = account + '.ics'
        cal = CurriculumCalendar(account, password, filename)
        if cal.student.HEADERS['token'] == '-1':
            flash('用户名或密码错误...', category='error')
            return render_template('login.html', form=MyForm())
        cal.gen_cal()
        directory = os.getcwd()
        response = make_response(send_from_directory(
            directory, filename, as_attachment=True))
        return response


@hut.route('/signout')
def signout():
    session.clear()
    return redirect(url_for('hut.login'))


@hut.route('/df', methods=['GET', 'POST'])
def electricity_fee_inquiry():
    elec = ElectricityFeeInquiry()
    if request.method == 'GET':
        xh = request.args.get('xh')
        ld = request.args.get('ld')
        qs = request.args.get('qs')
    else:
        xh = request.form.get('xh')
        ld = request.form.get('ld')
        qs = request.form.get('qs')
    print('%s-%s-%s' % (xh, ld, qs))
    if xh not in ('河东', '河西'):
        return "校区错误，可选值：河东、河西"
    else:
        if xh == '河东':
            areaid = '1016'
        else:
            areaid = '4'

    ld_data = elec.getJzinfo(2, 4)
    if ld not in ('36', '37', '38'):
        ld_name = '学生公寓' + str(ld) + '栋'
        qs_name = qs
    else:
        ld_name = '学生宿舍' + str(ld) + '栋'
        qs_name = ld + '-' + qs
    print(ld_name)
    if ld_data['code'] == 'SUCCESS':
        print(ld_data['msg'])
        # print(ld_data['roomlist'])
        buildid = None
        for room in ld_data['roomlist']:
            if ld_name == room['name']:
                buildid = room['id']
        if not buildid:
            return "未找到当前楼栋，请检查是否有错(输入数字即可，暂不支持非学生公寓查询)"
    else:
        return ld_data['msg']

    qs_data = elec.getJzinfo(4, areaid, buildid, -1)
    if qs_data['code'] == 'SUCCESS':
        print(qs_data['msg'])
        for room in qs_data['roomlist']:
            if qs_name == room['name']:
                qsid = room['id']
    else:
        return qs_data['msg']

    url = 'http://h5cloud.17wanxiao.com:8080/CloudPayment/user/getRoomState.do'
    params = {
        'payProId': elec.payProId,
        'schoolcode': 786,
        'businesstype': 2,
        'roomverify': qsid
    }
    req = requests.get(url, params=params,
                       timeout=5, headers=elec.HEADERS)
    res = json.loads(req.text)
    return (xh + '校区 ' + ld + '栋 ' + res['description'] + ' ' + '剩余电量：' + res['quantity'] + res['quantityunit'])


@hut.route('/job.ics', methods=['GET', 'POST'])
def gen_job_cal():
    if request.method == 'GET':
        suffix = request.args.get('sf')
        if(suffix == '宣讲会'):
            suffix = 'getcareers'
        elif(suffix == '双选会'):
            suffix = 'getjobfairs'
        elif(suffix):
            return("sf 值错误，可选值：'宣讲会'，'双选会'")
        else:
            suffix = 'getcareers'
        typ = request.args.get('tp')
        if(typ == '校内'):
            typ = 'inner'
        elif(typ == '校外'):
            typ = 'outer'
        elif(typ):
            return("tp 值错误，可选值：'校内'，'校外'")
        else:
            typ = 'inner'
    else:
        suffix = request.form.get('sf')
        if(suffix == '宣讲会'):
            suffix = 'getcareers'
        elif(suffix == '双选会'):
            suffix = 'getjobfairs'
        elif(suffix):
            return("sf 值错误，可选值：'宣讲会'，'双选会'")
        else:
            suffix = 'getcareers'

        typ = request.form.get('tp')
        if(typ == '校内'):
            typ = 'inner'
        elif(typ == '校外'):
            typ = 'outer'
        elif(typ):
            return("tp 值错误，可选值：'校内'，'校外'")
        else:
            typ = 'inner'

    job = JobCalendar(suffix=suffix)
    data = job.gen_cal(type=typ)
    response = make_response(data)
    response.headers['Content-Type'] = 'text/plain'
    return response
