# -*- coding=utf-8 -*-


"""
API 列表来源： https://github.com/TLingC/QZAPI_Archive
"""

import json
import sys
import uuid
from datetime import datetime, timedelta

import pytz
import os
import requests
# import getopt
# import getpass
from icalendar import Calendar, Event
from app import app
# import app.views

account = os.getenv('ACCOUNT')      # 账号
password = os.getenv('PASSWORD')    # 密码
url = 'http://218.75.197.123:83/app.do'     # 教务系统地址

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


class Student(object):
    def __init__(self, account, password):
        self.argv = sys.argv
        self.account = account      # 账号，默认使用全局变量 account
        self.password = password    # 密码，默认使用全局变量 password
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

        params = {
            "method": "authUser",
            "xh": self.account,
            "pwd": self.password
        }
        session = requests.Session()
        req = session.get(url, params=params,
                          timeout=5, headers=self.HEADERS)
        res = json.loads(req.text)
        self.HEADERS['token'] = res['token']
        return session

    def get_data(self, params):
        req = self.session.get(url, params=params,
                               timeout=5, headers=self.HEADERS)
        res = json.loads(req.text)
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
            "method": "getCurrentTime",
            "currDate": cur_time
        }
        res = self.get_data(params)
        return res

    def getKbcxAzc(self, zc=-1):
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
            "method": "getKbcxAzc",
            "xh": self.account,
            "xnxqid": xnxqid,
            "zc": s['zc'] if zc == -1 else zc
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

        parames = {"method": "getXqcx"}
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
            "method": "getJxlcx",
            "xqid": xqids
        }
        res = self.get_data(parames)
        return res

    def getKxJscx(self, js="0", idleTime="alday",  xqids="", jxlids="", classroomNumbers=""):
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

        if action in ["1", "2", "3"]:
            if action == "1":
                idleTime = "am"
            elif action == "2":
                idleTime = "pm"
            elif action == "3":
                idleTime = "night"

        params = {
            "method": "getKxJscx",
            "time": time,
            "idleTime": idleTime
        }

        js = input("是否启用精准查询? (默认不启用，0：No 1：Yes)")

        if js == "1":
            while True:
                xqids = input("请输入校区 ID:(1.河东校区  2.河西校区）")
                if xqids not in ["1", "2"]:
                    print("输入错误！请重新输入")
                else:
                    break
            while True:
                print(self.getJxlcx(xqids))
                jxlids = input("请输入教学楼 ID:")
                if jxlids not in ["01", "03", "04", "05", "06", "07", "08",
                                  "09", "10", "11", "12", "14", "16", "17",
                                  "18", "19", "20", "21", "22", "23", "24",
                                  "25", "26"]:
                    print("输入错误！请重新输入")
                else:
                    break
            params["xqid"] = xqids,
            params["jxlid"] = jxlids,
            params["classroomNumber"] = classroomNumbers

        res = self.get_data(params)
        return res

    def getUserInfo(self):
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
            'xh': self.account
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
            "method": "getCjcx",
            "xh": self.account,
            "xnxqid": id
        }
        res = self.get_data(params)
        return res

    def getKscx(self):
        """获取考试信息"""

        params = {
            "method": "getKscx",
            "xh": self.account
        }
        res = self.get_data(params)
        return res

    def gen_Kb_json_data(self):
        """
            生成所有课程的 json 数据
        """
        data = []
        for i in range(1, 31):
            res = self.getKbcxAzc(i)
            if res:
                # print('正在获取第 %d 周课表' % i)
                for j in res:
                    if j not in data:
                        data.append(j)
        return data

    def gen_Kb_web_data(self):
        """
            生成网页所需的总课表数据
        """
        data = {}
        kb = self.gen_Kb_json_data()
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


class My_Calendar(object):
    def __init__(self, filename='kb.ics', account=account, password=password, data=-1):
        self.account = account      # 账号，默认使用全局变量 account
        self.password = password    # 密码，默认使用全局变量 password
        self.student = Student(self.account, self.password)
        self.data = self.student.gen_Kb_json_data() if (data == -1) else data     # 所有课程的 json 数据
        self.start_date = self.get_start_date()    # 学期起始日期，格式为 %Y-%m-%d
        self.filename = filename        # 日历文件名

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
                s_week_s, e_week_s = j['kkzc'].split('-')
            except ValueError:
                s_week_s = j['kkzc']
                e_week_s = j['kkzc']
            self.start_date_datetime = datetime.strptime(self.start_date, "%Y-%m-%d") + \
                timedelta(days=(int(s_week_s)-1)*7+(int(j['kcsj'][:1]) - 1))
            end_date_datetime = self.start_date_datetime + \
                timedelta(days=(int(e_week_s)-1)*7+(int(j['kcsj'][:1]) - 1))
            s_year_s, s_mon_s, s_day_s = datetime.strftime(
                self.start_date_datetime, '%Y-%m-%d').split('-')
            e_year_s, e_mon_s, e_day_s = datetime.strftime(
                end_date_datetime, '%Y-%m-%d').split('-')

            s_hour_s, s_minu_s = j['kssj'].split(':')
            e_hour_s, e_minu_s = j['jssj'].split(':')

            # print("*"*50)
            # print(datetime(int(s_year_s), int(s_mon_s), int(
            #     s_day_s), int(s_hour_s), int(s_minu_s), 0))
            # print(datetime(int(s_year_s), int(s_mon_s), int(
            #     s_day_s), int(e_hour_s), int(e_minu_s), 0))
            # print("*"*50)
            # print(j)
            # print('>'*50)

            event.add('DTSTAMP', datetime.now())
            event.add('DTSTART', datetime(int(s_year_s), int(s_mon_s), int(s_day_s), int(s_hour_s), int(s_minu_s), 0,
                                          tzinfo=tz))
            event.add('DTEND', datetime(int(s_year_s), int(s_mon_s), int(s_day_s), int(e_hour_s), int(e_minu_s), 0,
                                        tzinfo=tz))
            event.add('SUMMARY', j['kcmc'])
            event.add('UID', str(uuid.uuid1()))
            event.add('LOCATION', '%s %s' %
                      (j['jsmc'], j['jsxm']))
            event.add('DESCRIPTION', '第%s节 - 第%s节\n%s\n%s' %
                      (j['kcsj'][2:3], j['kcsj'][-1:], j['jsmc'], j['jsxm']))
            parameters = {
                'FREQ': 'WEEKLY',
                'UNTIL': datetime(int(e_year_s), int(e_mon_s), int(e_day_s), int(e_hour_s), int(e_minu_s), 0,
                                  tzinfo=tz),
                'INTERVAL': '1'
            }
            event.add('RRULE', parameters)
            cal.add_component(event)
        # print(str(cal.to_ical(), encoding='utf8'))

        with open(self.filename, 'w', encoding='utf8') as f:
            f.write(str(cal.to_ical(), encoding='utf8'))


if __name__ == '__main__':
    # test = Student(account, password)
    # a = test.get_current_time()
    # t = My_Calendar()
    # t.gen_cal()
    # with open('kb.json', 'w', encoding='utf8') as f:
    #     json.dump(t.gen_Kb_json_data(), f, ensure_ascii=False)
    app.run()
