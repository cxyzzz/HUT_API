from flask import redirect, render_template, request
from app import app
import json
from HUT import Student


@app.route('/')
def index():
    data = {}
    kb = json.load(open('kb.json', 'r', encoding='utf8'))
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
    print(data)
    return render_template('index.html', **data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        account = request.form.get("account", type=str, default=None)
        password = request.form.get("password", type=str, default=None)
    except ValueError as verr:
        print('*'*50)
        print(verr)
        print('*'*50)
    print('-'*50)
    print('%s %s' % (account, password))
    print('-'*50)

    test = Student(account, password)
    data = []
    tmp = []

    for i in range(1, 31):
        res = test.getKbcxAzc('%d' % i)
        if res:
            print('正在获取第 %s 周课表数据' % i)
            for j in res:
                tmp.append(j)
    for i in tmp:
        if i not in data:
            data.append(i)

    print('正在处理数据')

    with open('kb.json', 'w',  encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False)

    return redirect('/')


@app.route('/test')
def test():
    return 'test'
