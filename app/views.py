import os
from app.feed import SchoolFeed, JobFeed
from datetime import timedelta, datetime
from flask import (Blueprint, flash, make_response, redirect, render_template,
                   request, send_from_directory, session, url_for)
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import InputRequired
import app
from app.HUT import Student, CurriculumCalendar, ElectricityFeeInquiry, JobCalendar

# app = create_app()
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
            account = request.form.get('account', type=str, default=None)
            password = request.form.get('password', type=str, default=None)
            student = Student(account, password)
            if student.HEADERS['token'] == '-1':
                flash('用户名或密码错误...', category='error')
                return render_template('login.html', form=form)
            if(request.form.get('remember') == '1'):
                session.permanent = True
                app.permanent_session_lifetime = timedelta(hours=1)
            session['account'] = account
            session['password'] = password
            # print(session)
            return redirect(url_for('hut.index'))
        # print('*'*50)
        return redirect(url_for('hut.login'))


@hut.route('/', methods=['GET'])
def index():
    if (session.get('account') and session.get('password')):
        account = session['account']
        password = session['password']
        student = Student(account, password)
        if student.HEADERS['token'] == '-1':
            flash('用户名或密码错误...', category='error')
            return render_template('login.html', form=MyForm())
        xh = request.args.get('xh')
        if xh != session.get('xh'):
            session['xh'] = xh
            session['data'] = student.gen_Kb_json_data(xh)
        if not session.get('data'):
            session['data'] = student.gen_Kb_json_data(xh)
        # print(session)
        data = student.gen_Kb_web_data(kb=session['data'], xh=xh)
        print(data['user'])
        return render_template('index.html', **data)
    else:
        return redirect(url_for('hut.login'))


@hut.route('/gen_cal', methods=['GET'])
def gen_cur_cal():
    if session.get('data'):
        account = session['account']
        password = session['password']
        filename = account + '.ics'
        cal = CurriculumCalendar(account, password, filename, session['data'])

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
        xq = request.args.get('xq')
        ld = request.args.get('ld')
        qs = request.args.get('qs')
    else:
        xq = request.form.get('xq')
        ld = request.form.get('ld')
        qs = request.form.get('qs')
    return elec.query(xq=xq, ld=ld, qs=qs)


@hut.route('/job.ics', methods=['GET'])
def gen_job_cal():
    """
        :args school mode, style, type
    """

    kwargs = request.args.to_dict()
    school = kwargs.get('school', 'hngydx')
    if (school and school not in JobCalendar.SCHOOL_LIST.keys()):
        return ("school 值错误，默认：hngydx，目前可选值：（如果确定你的学校使用的是一样的系统而列表里没有欢迎提交给我进行适配）\n{school_list}".format(JobCalendar.SCHOOL_LIST))

    mode = kwargs.get('mode', 'getcareers')
    mode_tuple = ('getcareers, getjobfairs')
    if(mode and mode not in mode_tuple):
        return("mode 值错误，可选值：getcareers(默认), getjobfairs")

    type_ = kwargs.get('type', 'inner')
    if(mode in ('getcareers, getjobfairs')):
        if(type_ and type_ not in ('inner', 'outer')):
            return("type 值错误，可选值：inner(默认), outer")

    style = kwargs.get('style', 'simple')
    if(style and style not in ('simple', 'full')):
        return("style 值错误，可选值：simple(默认), full")

    file_name = '{0}_{1}_jb.ics'.format(school, mode)
    # return(file_name)
    try:
        file_timstamp = os.path.getmtime(file_name)
        file_timeinfo = datetime.fromtimestamp(file_timstamp)
    except FileNotFoundError:
        job = JobCalendar(**kwargs)
        data = job.gen_cal(**kwargs)
        if(not data):
            return("暂无数据！")
        response = make_response(data)
        # response.headers["Content-Disposition"] = "attachment; filename=job_calendar.ics"
        return response
    now_hour = datetime.now().hour
    if (now_hour - file_timeinfo.hour >= 1):
        job = JobCalendar(**kwargs)
        data = job.gen_cal(**kwargs)
        if(not data):
            return("暂无数据！")
        response = make_response(data)
        # response.headers["Content-Disposition"] = "attachment; filename=job_calendar.ics"
        return response
    else:
        directory = os.getcwd()
        response = make_response(send_from_directory(
            directory, file_name, mimetype='text/plain'))
        response.headers['Content-Type'] = 'text/plain; charset=UTF-8'
        return response


@hut.route('/feed', methods=['GET'])
def school_feed():
    type_ = request.args.get('type')
    if(type_):
        type_ = int(type_)
    customerId = request.args.get('customerId')

    if (type_ not in (2, 3)):
        type_ = 3

    if (customerId not in range(784, 869)):
        customerId = 786

    if (type_ == 2):
        name = "校内新闻"
    else:
        name = "通知公告"
    file_name = name + '_feed.xml'

    try:
        file_timstamp = os.path.getmtime(file_name)
        file_timeinfo = datetime.fromtimestamp(file_timstamp)
    except FileNotFoundError:
        school = SchoolFeed(type_=type_, customerId=customerId)
        rss = school.gen_feed()
        response = make_response(rss)
        response.headers['Content-Type'] = 'application/xml; charset=UTF-8'
        return response

    now_hour = datetime.now().hour
    if (now_hour - file_timeinfo.hour >= 1):
        school = SchoolFeed(type_=type_, customerId=customerId)
        rss = school.gen_feed()
        response = make_response(rss)
        response.headers['Content-Type'] = 'application/xml; charset=UTF-8'
        return response
    else:
        directory = os.getcwd()
        response = make_response(send_from_directory(
            directory, file_name, mimetype='application/xml'))
        response.headers['Content-Type'] = 'application/xml; charset=UTF-8'
        return response


@hut.route('/jobfeed', methods=['GET'])
def job_feed():
    kwargs = request.args.to_dict()

    school = kwargs.get('school', 'hngydx')
    if (school and school not in JobCalendar.SCHOOL_LIST.keys()):
        return ("school 值错误，默认：hngydx，目前可选值：（如果确定你的学校使用的是一样的系统而列表里没有欢迎提交给我进行适配）\n{school_list}".format(JobCalendar.SCHOOL_LIST))
    school_name = JobCalendar.SCHOOL_LIST[school]

    mode = kwargs.get('mode', 'getonlines')
    mode_tuple = ('getonlines, getjobs')
    if(mode and mode not in mode_tuple):
        return("mode 值错误，可选值：getonlines(默认), getjobs")

    if (mode == 'getonlines'):
        mode_name = '在线招聘'
    elif(mode == 'getjobs'):
        mode_name = "岗位招聘"
    else:
        kwargs['mode'] = 'getonlines'
        mode_name = '在线招聘'
    kwargs['style'] = 'full'
    kwargs['mode'] = 'getonlines'
    file_name = school_name + mode_name + '_feed.xml'
    print(kwargs)
    try:
        file_timstamp = os.path.getmtime(file_name)
        file_timeinfo = datetime.fromtimestamp(file_timstamp)
    except FileNotFoundError:
        job = JobFeed(**kwargs)
        rss = job.gen_feed()
        response = make_response(rss)
        response.headers['Content-Type'] = 'application/xml; charset=UTF-8'
        return response

    now_hour = datetime.now().hour
    if (now_hour - file_timeinfo.hour >= 1):
        job = JobFeed(**kwargs)
        rss = job.gen_feed()
        response = make_response(rss)
        response.headers['Content-Type'] = 'application/xml; charset=UTF-8'
        return response
    else:
        directory = os.getcwd()
        response = make_response(send_from_directory(
            directory, file_name, mimetype='application/xml'))
        response.headers['Content-Type'] = 'application/xml; charset=UTF-8'
        return response
