# -*- coding=utf-8 -*-


"""
API 列表来源： https://github.com/TLingC/QZAPI_Archive
"""

import json
import os
import sqlite3
import threading
# mport sys
import time
import uuid
from datetime import datetime, timedelta
from random import randint

import pytz
import requests
# import getopt
# import getpass
from icalendar import Calendar, Event

# def get_username_password(self):
#     """
#     解析命令行参数 得到用户名和密码
#     """

#     try:
#         opts, args = getopt.getopt(
#             self.argv[1:], 'hu:p:', ['username=', 'password='])
#     except getopt.GetoptError:
#         print('你的打开方式不对！请重新输入命令')
#         print('HUT.py -u <username> -p <password>')
#         sys.exit(-1)
#     for opt, arg in opts:
#         if opt in ('-h', '--help', 'help'):
#             print('usage: python %s -')
#         if opt in ('-u', '--username'):
#             self.username = arg
#         elif opt in ('-p', '--password'):
#             self.password = arg
#     if "username" not in locals().keys():
#         self.username = input("请输入学号：")
#     if "password" not in locals().keys():
#         self.password = getpass.getpass("请输入密码（无回显）：")


class SqliteDb(object):
    def __init__(self, filename='HUT.db'):
        self.conn = sqlite3.connect(filename)
        print("Opened database successfully")
        self.cur = self.conn.cursor()
        try:
            self.cur.execute('''CREATE TABLE STUDENT
                    (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    RXNF        CHAR(5);
                    NJ          CHAR(5),
                    YXMC        CHAR(30),
                    ZYMC        CHAR(15),
                    BJ          CHAR(15),
                    XH          CHAR(15)    NOT NULL,
                    XM          TEXT    NOT NULL,
                    XB          TEXT     NOT NULL,
                    DH          CHAR(15),
                    EMAIL       CHAR(30),
                    KSH         CHAR(15));
                    ''')
            print("Table created successfully")
            self.conn.commit()
        except sqlite3.OperationalError as err:
            print(err)
            # sys.exit(0)

    def insert(self, data):
        # return
        execute = ('''INSERT INTO STUDENT (NJ,YXMC,ZYMC,BJ,XH,XM,XB,DH,EMAIL,KSH)
        VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')''' % (
            data['nj'], data['yxmc'], data['zymc'], data['bj'], data['xh'], data['xm'], data['xb'], data['dh'], data['email'], data['ksh']))
        self.cur.execute(execute)
        self.conn.commit()

    def xh_search(self, xh):
        execute = ("select xh from student where xh is %s" % (xh))
        self.cur.execute(execute)
        return self.cur.fetchall()


class MyThread(threading.Thread):
    def __init__(self, func, *args, **kwargs):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.result = self.func(*self.args, **self.kwargs)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None


class Student(object):
    def __init__(self, account=-1, password=-1):
        self.account = os.getenv(
            'xh') if account == -1 else account      # 账号，默认使用全局变量 account
        self.password = os.getenv(
            'pwd') if password == -1 else password   # 密码，默认使用全局变量 password
        self.session = self.login()

    HEADERS = {
        'User-Agent': ('Mozilla/5.0 (Linux; Android 9; Redmi Note 7 Build/PKQ1.180904.001; wv) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 '
                       'Chrome/67.0.3396.87 XWEB/882 MMWEBSDK/190503 '
                       'Mobile Safari/537.36 MMWEBID/443 '
                       'MicroMessenger/7.0.5.1440(0x27000536) '
                       'Process/tools NetType/4G Language/zh_CN '
                       'MicroMessenger/7.0.5.1440(0x27000536) '
                       'Process/tools NetType/4G Language/zh_CN miniProgram'),
        'Referer': 'http://218.75.197.123:83',
        'accept-encoding': 'gzip, deflate, br'
    }

    URL = 'http://218.75.197.123:83/app.do'     # 教务系统地址

    def login(self):
        """ 登录
            返回值:
                {
                    'success': 登录状态,
                    'token': 'Token',
                    'user':{
                        'scsj': None,
                        'sjyzm': None,
                        'useraccount': '登录用户',
                        'usertype': '用户类型，学生为 2',
                        'userdwmc': '学院',
                        'username': '用户姓名',
                        'userpasswd': '用户密码'
                        },
                    'userdwmc': '学院',
                    'userrealname': '用户姓名',
                    'usertype': '用户类型，学生为 2'

                }
        """

        datas = {
            'method': 'authUser',
            'xh': self.account,
            'pwd': self.password
        }
        session = requests.Session()
        res = session.post(self.URL, data=datas,
                           timeout=5, headers=self.HEADERS)
        res = res.json()
        if res['success']:
            self.HEADERS['token'] = res['token']
            return session
        else:
            print(res['msg'])
            exit(0)

    def get_data(self, params):
        try:
            res = self.session.get(self.URL, params=params,
                                   timeout=5, headers=self.HEADERS)
            res = res.json()
        except Exception as err:
            time.sleep(1)
            print(err)
        return res

    def get_current_time(self):
        """ 获取当前时间、周次、学年等信息
            返回数据：
                {
                    'e_time': '周结束时间',
                    's_time': '周开始时间',
                    'xnxqh': '学年',
                    'zc': '周次'
                }
        """

        cur_time = datetime.strftime(
            datetime.now(), '%Y-%m-%d')
        params = {
            'method': 'getCurrentTime',
            'currDate': cur_time
        }
        res = self.get_data(params)
        return res

    def getKbcxAzc(self, zc=''):
        """ 课表查询,默认查询当前周
            返回数据：
                [
                    {
                        'jsmc': '教室名称',
                        'jssj': '下课时间',
                        'jsxm': '教师姓名',
                        'kcmc': '课程名称',
                        'kkzc': '课程教学周',
                        'kcsj': '课程时间（eg: 50304 表示星期五第3-4节）',
                        'kssj': '上课时间',
                        'sjbz': '未知'
                    }
                ]
        """
        s = self.get_current_time()
        xnxqid = s['xnxqh']
        params = {
            'method': 'getKbcxAzc',
            'xh': self.account,
            'xnxqid': xnxqid,
            'zc': s['zc'] if not zc else zc
        }
        res = self.get_data(params)
        return res

    def getXqcx(self):
        """ 获取校区 ID
            返回值：
                [
                    {
                        'xqid': '1',
                        'xqmc': '河东校区'
                    },
                    {
                        'xqid': '2',
                        'xqmc': '河西校区'
                    }
                ]
        """

        parames = {'method': 'getXqcx'}
        res = self.get_data(parames)
        return res

    def getJxlcx(self, xqids):
        """ 获取校区教学楼信息
            返回值：
                [
                    {
                        'jzwid': '教学楼 ID',
                        'jzwmc': '教学楼名称'
                    }
                ]
        """

        parames = {
            'method': 'getJxlcx',
            'xqid': xqids
        }
        res = self.get_data(parames)
        return res

    def getKxJscx(self, js='0', idleTime='alday',  xqids='', jxlids='', classroomNumbers=''):
        """ 空教室查询
            idleTime取值
                allday：全天
                am：上午
                pm：下午
                night：晚上

            精确查询空教室 (xqid: 校区 id、jxlid: 教学楼 id、classroomNumber： 教室人数)
            classroomNumber
                30：30人以下
                30-40：30-40人
                40-50：40-50人
                60：60人以上
            返回值：
                {
                    'data': [
                        {
                            'jsList': [
                                {
                                    'jsh': '未知',
                                    'jsid': '教室 ID',
                                    'jsmc': '教室名称',
                                    'jzwid': '所在楼ID',
                                    'jzwmc': '教学楼名称',
                                    'xqmc': '校区名称',
                                    'yxzws': 教室容量,
                                    'zws': 未知，和yxzws相同
                                }
                            ],
                            'jxl': '教学楼'
                        }
                    ],
                    'success': 状态,
                    'xnxqid': '学年'
                }
        """

        date = input("请输入查询日期： （格式为 XXXX-XX-XX,默认为当前日期）")
        cur_time = datetime.strftime(
            datetime.now(), '%Y-%m-%d')
        time = date if len(date) != 0 else cur_time

        action = input("请输入查询时间： 1.上午  2.下午  3.晚上（默认为全天，只需输入数字）")
        print("您选择的操作：%s" % action)

        if action in ['1', '2', '3']:
            if action == '1':
                idleTime = 'am'
            elif action == '2':
                idleTime = 'pm'
            elif action == '3':
                idleTime = 'night'

        params = {
            'method': 'getKxJscx',
            'time': time,
            'idleTime': idleTime
        }

        js = input("是否启用精准查询? (默认不启用，0：No 1：Yes)")

        if js == '1':
            while True:
                xqids = input("请输入校区 ID:(1.河东校区  2.河西校区）")
                if xqids not in ['1', '2']:
                    print("输入错误！请重新输入")
                else:
                    break
            while True:
                print(self.getJxlcx(xqids))
                jxlids = input("请输入教学楼 ID:")
                if jxlids not in ['01', '03', '04', '05', '06', '07', '08',
                                  '09', '10', '11', '12', '14', '16', '17',
                                  '18', '19', '20', '21', '22', '23', '24',
                                  '25', '26']:
                    print("输入错误！请重新输入")
                else:
                    break
            params['xqid'] = xqids,
            params['jxlid'] = jxlids,
            params['classroomNumber'] = classroomNumbers

        res = self.get_data(params)
        return res

    def getUserInfo(self, xh=''):
        ''' 获取帐号信息
            返回值：
                {
                    'bj': '班级',
                    'dh': '电话',
                    'dqszj': '未知，与入学年份、年级相同',
                    'email': '电子邮箱',
                    'fxzy': '辅修专业',
                    'ksh': '高考考号',
                    'nj': '年级',
                    'qq': 'QQ 号',
                    'rxnf': '入学年份',
                    'usertype': '用户类别，学生为 2',
                    'xb': '性别',
                    'xh': '学号',
                    'xm': '姓名',
                    'xz': 未知,
                    'yxmc'：'院系名称',
                    'zymc'：'专业名称'
                }
        '''

        params = {
            'method': 'getUserInfo',
            'xh': self.account if not xh else xh
        }
        res = self.get_data(params)
        return res

    def getXnxq(self):
        ''' 获取学年和学期信息
            返回值：
                [
                    {
                        'isdqxq': '是否为当前学期，1 为是，0 为否',
                        'xnxq01id': '学年id',
                        'xqmc': '学年名称'
                    }
                ]
        '''

        params = {
            'method': 'getXnxq',
            'xh': self.account
        }
        res = self.get_data(params)
        return res

    def getCjcx(self, id=''):
        """ 获取成绩信息
                返回值：
                    {
                        'result': [
                            {
                                'bz': 未知,
                                'cjbsmc': 未知,
                                'kclbmc': '课程类别名称',
                                'kcmc': '课程名称',
                                'kcxzmc': '课程性质名称',
                                'kcywmc': 未知,
                                'ksxzmc': '考试性质名称',
                                'xf': 学分,
                                'xm': '姓名',
                                'xqmc': '学期名称',
                                'zcj': '总成绩'
                            }
                        ]，
                        'success': 状态
                    }
        """

        params = {
            'method': 'getCjcx',
            'xh': self.account,
            'xnxqid': id
        }
        res = self.get_data(params)
        return res

    def getKscx(self):
        """获取考试信息"""

        params = {
            'method': 'getKscx',
            'xh': self.account
        }
        res = self.get_data(params)
        return res

    def gen_Kb_json_data(self):
        """
            生成所有课程的 json 数据
        """
        data = []
        for i in range(1, 31):
            t = MyThread(self.getKbcxAzc, (i,))
            t. start()
            t.join()
            res = t.get_result()
            if res:
                print('正在获取第 %d 周课表' % i)
                for j in res:
                    if j not in data:
                        data.append(j)
        return data

    def gen_Kb_web_data(self, kb=()):
        """
            生成网页所需的总课表数据
        """
        data = {}
        kb = self.gen_Kb_json_data() if not kb else kb

        for i in range(1, 8):
            for j in range(1, 8):
                data['kb' + str(i)+'_'+str(j)] = '&nbsp;'
        for i in kb:
            dic_key = 'kb' + i['kcsj'][0:1]+'_' + \
                str(int((int(i['kcsj'][2:3])+int(i['kcsj'][4:])+1)/4))
            if data[dic_key] != '&nbsp;':
                m = data[dic_key]['multy']
                m += 1
                data[dic_key]['multy'] = m
                data[dic_key]['multy' + str(m)] = {
                    'kcmc': i['kcmc'],
                    'jsxm': i['jsxm'],
                    'kkzc': i['kkzc'],
                    'jsmc': i['jsmc']
                }
            else:
                data[dic_key] = {
                    'multy': 0,
                    'kcmc': i['kcmc'],
                    'jsxm': i['jsxm'],
                    'kkzc': i['kkzc'],
                    'jsmc': i['jsmc']
                }
        data['user'] = self.getUserInfo()
        return data

    def gen_user_db(self, db):
        self.db = db
        data = {
            'method': 'getUserInfo'
        }
        njs = ('19', '18', '17', '16')
        bj = 0
        id = 0
        xy_list = json.load(open('学院.json', 'r'))
        xy_zys = []
        for xy in xy_list:
            for id in xy['ids']:
                for zy in id['zy']:
                    xy_zys.append((id['id'], zy['id']))
        for nj in njs:
            print(nj)
            for xy_zy in xy_zys:
                print(xy_zy)
                # time.sleep(5)
                if(nj == '17' and xy_zy[0] == '408' and xy_zy[1] == '00'):
                    bj = 10
                while(True):
                    data['xh'] = str(nj) + xy_zy[0] + xy_zy[1] + \
                        str(bj).zfill(2) + str(id).zfill(2)
                    if(not self.db.xh_search(data['xh'])):
                        t = MyThread(self.get_data, (data,))
                        t.start()
                        t.join()
                        res = t.get_result()
                    else:
                        res = 'break'
                    if(res):
                        # 有数据表明当前班级号正确
                        if(res != 'break'):
                            print('Insert=====>', res)
                            self.db.insert(res)
                        # print(res)
                        # 获取此班级所有学生
                        while(True):
                            id += 1
                            if(xy_zy[1] == '00' or xy_zy[1] == '11' or xy_zy[1] == '15' or xy_zy[1] == '70' or xy_zy[0] == '110'):
                                if(id % 30 == 0):
                                    print('long id sleep %.2f' %
                                          (id/100))
                                    time.sleep(id/100)
                            data['xh'] = str(
                                nj) + xy_zy[0] + xy_zy[1] + str(bj).zfill(2) + str(id).zfill(2)
                            if(not self.db.xh_search(data['xh'])):
                                t = MyThread(self.get_data, (data,))
                                t.start()
                                t.join()
                                res = t.get_result()
                            else:
                                res = 'break'
                            if(res):
                                # 有数据表明当前班级号正确
                                if(res != 'break'):
                                    print('Insert=====>', res)
                                    self.db.insert(res)
                                    # print(res)
                            else:
                                break
                    else:
                        # 防止当某个班级没有 00 这个编号时出现直接跳过此班级的情况
                        while(True):
                            id += 1
                            if(xy_zy[1] == '00' or xy_zy[1] == '11' or xy_zy[1] == '15' or xy_zy[1] == '70' or xy_zy[0] == '110'):
                                if(id % 30 == 0):
                                    print('long id sleep %.2f' %
                                          (id/100))
                                    time.sleep(id/100)
                            data['xh'] = str(
                                nj) + xy_zy[0] + xy_zy[1] + str(bj).zfill(2) + str(id).zfill(2)
                            if(not self.db.xh_search(data['xh'])):
                                t = MyThread(self.get_data, (data,))
                                t.start()
                                t.join()
                                res = t.get_result()
                            else:
                                res = 'break'
                            if(res):
                                # 有数据表明当前班级号正确
                                if(res != 'break'):
                                    print('Insert=====>', res)
                                    self.db.insert(res)
                                    # print(res)
                            else:
                                break
                        # 跑完一个班级，班级号加一，班级编号重置为0
                        bj += 1
                        # 处理4080012 之后直接调到 4080020
                        if(nj == '17' and xy_zy[0] == '408' and xy_zy[1] == '00'):
                            if(bj == 13):
                                bj = 20
                        id = 0
                        data['xh'] = str(nj) + xy_zy[0] + xy_zy[1] + \
                            str(bj).zfill(2) + str(id).zfill(2)
                        t = MyThread(self.get_data, (data,))
                        t.start()
                        t.join()
                        res = t.get_result()
                        # 防止当班级加一后无00编号导致直接跳过此专业
                        if(not res):
                            id += 1
                            data['xh'] = str(nj) + xy_zy[0] + xy_zy[1] + \
                                str(bj).zfill(2) + str(id).zfill(2)
                        if(not res and not self.get_data(data)):
                            # 无数据表明已跑完此专业所有班级，将班级号和班级编号置0(17级计算机班级从10开始)，跳出循环进行下一个专业查询
                            if(nj == '17' and xy_zy[0] == '408' and xy_zy[1] == '00'):
                                bj = 10
                            else:
                                bj = 0
                            id = 0
                            break
        self.db.conn.close()


class CurriculumCalendar(object):
    def __init__(self, account=-1, password=-1, filename='kb.ics', data=()):
        self.account = os.getenv(
            'ACCOUNT') if account == -1 else account      # 账号，默认使用全局变量 account
        self.password = os.getenv(
            'PASSWORD') if password == -1 else password   # 密码，默认使用全局变量 password
        self.student = Student(self.account, self.password)
        self.start_date = self.get_start_date()    # 学期起始日期，格式为 %Y-%m-%d
        self.filename = filename        # 日历文件名
        self.data = self.student.gen_Kb_json_data() if (
            not data) else data   # 所有课程的 json 数据

    def get_start_date(self):
        res = self.student.get_current_time()
        start_date_datetime = datetime.strptime(res['s_time'], "%Y-%m-%d") \
            - timedelta(days=(int(res['zc'])-1)*7)
        return datetime.strftime(
            start_date_datetime, '%Y-%m-%d')

    def gen_cal(self):
        """
            生成日历文件，文件名为 self.filename，路径为当前路径
        """

        tz = pytz.timezone('Asia/Shanghai')

        cal = Calendar()
        cal.add('PRODID', '-//Hoshizora //iCalendar 4.0.3')
        cal.add('VERSION', '2.0')
        cal.add('CALSCALE', 'GREGORIAN')
        # print(self.data)
        for j in self.data:
            event = Event()
            try:
                sta_week, end_week = j['kkzc'].split('-')
            except ValueError:
                sta_week = j['kkzc']
                end_week = j['kkzc']
            self.start_date_datetime = datetime.strptime(self.start_date, "%Y-%m-%d") + \
                timedelta(days=(int(sta_week)-1)*7+(int(j['kcsj'][:1]) - 1))
            end_date_datetime = self.start_date_datetime + \
                timedelta(days=(int(end_week)-1)*7+(int(j['kcsj'][:1]) - 1))
            sta_year, sta_mon, sta_day = datetime.strftime(
                self.start_date_datetime, '%Y-%m-%d').split('-')
            end_year, end_mon, end_day = datetime.strftime(
                end_date_datetime, '%Y-%m-%d').split('-')

            sta_hour, sta_minu = j['kssj'].split(':')
            end_hour, end_minu = j['jssj'].split(':')

            # print("*"*50)
            # print(datetime(int(sta_year), int(sta_mon), int(
            #     sta_day), int(sta_hour), int(sta_minu), 0))
            # print(datetime(int(sta_year), int(sta_mon), int(
            #     sta_day), int(end_hour), int(end_minu), 0))
            # print("*"*50)
            # print(j)
            # print('>'*50)

            event.add('DTSTAMP', datetime.now())
            event.add('DTSTART', datetime(int(sta_year), int(sta_mon), int(sta_day), int(sta_hour), int(sta_minu), 0,
                                          tzinfo=tz))
            event.add('DTEND', datetime(int(sta_year), int(sta_mon), int(sta_day), int(end_hour), int(end_minu), 0,
                                        tzinfo=tz))
            event.add('SUMMARY', j['kcmc'])
            event.add('UID', str(uuid.uuid1()))
            event.add('LOCATION', '%s %s' %
                      (j['jsmc'], j['jsxm']))
            event.add('DESCRIPTION', '第%s节 - 第%s节\n%s\n%s' %
                      (j['kcsj'][2:3], j['kcsj'][-1:], j['jsmc'], j['jsxm']))
            parameters = {
                'FREQ': 'WEEKLY',
                'UNTIL': datetime(int(end_year), int(end_mon), int(end_day), int(end_hour), int(end_minu), 0,
                                  tzinfo=tz),
                'INTERVAL': '1'
            }
            event.add('RRULE', parameters)
            cal.add_component(event)
        # print(str(cal.to_ical(), encoding='utf8'))

        with open(self.filename, 'w', encoding='utf8') as f:
            f.write(str(cal.to_ical(), encoding='utf8'))


class ElectricityFeeInquiry(object):
    URL = 'http://h5cloud.17wanxiao.com:8080/CloudPayment/user/getRoom.do'
    HEADERS = {
        'User-Agent': ('Mozilla/5.0 (Linux; Android 8.0.0; SM-G960F Build/PKQ1.180904.001; wv) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 '
                       'Chrome/74.0.3729.157 Mobile Safari/537.36 Wanxiao/5.0.2'),
        'Referer': 'http://h5cloud.17wanxiao.com:8080/CloudPayment/bill/selectPayProject.do?txcode=elecdetails&interurl=elecdetails&payProId=1567&amtflag=0&payamt=0&payproname=%E8%B4%AD%E7%94%B5%E6%94%AF%E5%87%BA&img=https://cloud.59wanmei.com:8443/CapecYunPay/images/project/img-nav_2.png&subPayProId=',
        'accept-encoding': 'gzip, deflate'
    }

    def __init__(self):
        self.payProId = randint(1, 10000)

    def get_data(self, params):
        req = requests.get(self.URL, params=params,
                           timeout=5, headers=self.HEADERS)
        res = json.loads(req.text)
        return res

    def getJzinfo(self, optype=1, arieaid=0, buildid=0, levelid=0):
        """
            获取编号
            arieaid: 校区 id
            buildid： 楼栋 id
        """
        params = {
            'payProId': self.payProId,
            'schoolcode': 786,
            'optype': optype,
            'areaid': arieaid,
            'buildid': buildid,
            'unitid': 0,
            'levelid': levelid,
            'businesstype': 2
        }
        res = self.get_data(params)
        return res


class JobCalendar(object):
    HOST = 'http://job.hut.edu.cn/module/'
    INFO_HOST = 'http://static.bibibi.net/student/chance/preachmeetingdetails.html?token=yxqqnn0000000012&career_id='
    INFO_API_HOST = 'http://student.bibibi.net/index.php?r=career/ajaxgetcareerdetail&token=yxqqnn0000000012&career_id='
    HEADERS = {
        'User-Agent': ('Mozilla/5.0 (Linux; Android 9; Redmi Note 7 Build/PKQ1.180904.001; wv) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 '
                       'Chrome/67.0.3396.87 XWEB/882 MMWEBSDK/190503 '
                       'Mobile Safari/537.36 MMWEBID/443 '
                       'MicroMessenger/7.0.5.1440(0x27000536) '
                       'Process/tools NetType/4G Language/zh_CN '
                       'MicroMessenger/7.0.5.1440(0x27000536) '),
    }

    def __init__(self, suffix='getcareers', m=14):
        self.suffix = suffix
        self.url = self.HOST + suffix
        self.dates = []
        for i in range(m):
            self.dates.append(datetime.strftime(datetime.now() + timedelta(days=i), '%Y-%m-%d'))
        self.cal = Calendar()
        self.session = requests.Session()

    def get_datas(self, **kwargs):
        params = {
            'start': kwargs['start'] if('start' in kwargs.keys()) else 0,
            'count': kwargs['count'] if('count' in kwargs.keys()) else 100,
            'keyword': kwargs['keyword'] if('keyword' in kwargs.keys()) else '',
            'address': kwargs['address'] if('address' in kwargs.keys()) else '',
            'type': kwargs['type'] if('type' in kwargs.keys()) else 'inner'
        }
        if(self.suffix == 'getcareers'):
            params['professionals'] = kwargs['professionals'] if('professionals' in kwargs.keys()) else ''
            params['career_type'] = kwargs['career_type'] if('career_type' in kwargs.keys()) else ''
            self.HEADERS['Referer'] = 'http://job.hut.edu.cn/module/careers'
        else:
            params['organisers'] = kwargs['organisers'] if('organisers' in kwargs.keys()) else ''
            param['type'] = None if(param['type'] == 'inner') else 2
            self.HEADERS['Referer'] = 'http://job.hut.edu.cn/module/jobfairs'

        datas = []
        for date in self.dates:
            params['day'] = date
            while(True):
                try:
                    t = MyThread(self.session.get, self.url, params=params,
                                 timeout=5, headers=self.HEADERS)
                    t.start()
                    t.join()
                    res = t.get_result()
                    # print(res.url)
                    res = res.json()
                    # print('>' * 50)
                    # print(res)
                    if(res['data']):
                        datas.append(res['data'][0])
                        # time.sleep(0.5)
                    break
                except Exception as err:
                    print(err)
                    time.sleep(1)
            if(not res['data']):
                break
        return datas

    def gen_cal(self, **kwargs):
        tz = pytz.timezone('Asia/Shanghai')

        cal = Calendar()
        cal.add('PRODID', '-//Hoshizora //iCalendar 4.0.3')
        cal.add('VERSION', '2.0')
        cal.add('CALSCALE', 'GREGORIAN')
        # print(self.data)
        for data in self.get_datas(**kwargs):
            year, mon, day = data['meet_day'].split('-')
            sta_hour, sta_minu = data['meet_time'].split(':')
            event = Event()
            event.add('DTSTAMP', datetime.now())
            event.add('DTSTART', datetime(int(year), int(mon), int(day), int(sta_hour), int(sta_minu), 0,
                                          tzinfo=tz))
            # event.add('DTEND', datetime(int(year), int(mon), int(day), int(sta_hour)+2, int(sta_minu), 0,
            #                             tzinfo=tz))
            event.add('SUMMARY', data['meet_name'])
            event.add('UID', str(uuid.uuid1()))
            event.add('LOCATION', data['address'])
            event.add('DESCRIPTION', '%s %s %s\n城市：%s 点击统计：%s\n企业属性：%s 行业类别: %s\n需求专业：%s\n%s' %
                      (data['meet_day'], data['meet_time'], data['address'],
                       data['city_name'], data['view_count'],
                       data['company_property'], data['industry_category'],
                       data['professionals'],
                       self.INFO_HOST + data['career_talk_id']))
            # parameters = {
            #     'FREQ': 'WEEKLY',
            #     'UNTIL': datetime(int(year), int(mon), int(day), int(sta_hour) + 2, int(sta_minu), 0,
            #                       tzinfo=tz),
            #     'INTERVAL': '1'
            # }
            # event.add('RRULE', parameters)
            cal.add_component(event)
        # s = str(cal.to_ical(), encoding='utf8')
        # print(s)
        return(str(cal.to_ical(), encoding='utf8'))
        # with open('jb.ics', 'w', encoding='utf8') as f:
        #     f.write(str(cal.to_ical(), encoding='utf8'))


if __name__ == '__main__':
    t = JobCalendar()
    t.get_datas()
    pass
