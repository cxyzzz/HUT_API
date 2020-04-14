import datetime
import re
from xml.dom.minidom import Document

import requests


class SchoolFeed(object):
    # 生成学校校内新闻和通知公告 RSS

    HOST = 'https://www.17wanxiao.com'
    UserAgent = ('Mozilla/5.0 (Linux; U; Android 9; zh-CN; Redmi Note 7 Build/PKQ1.180904.001) '
                 'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 '
                 'Chrome/69.0.3497.100 UWS/3.21.0.119 Mobile Safari/537.36 '
                 'AlipayChannelId/5136 UCBS/3.21.0.119_200318195923 '
                 'NebulaSDK/1.8.100112 Nebula AlipayDefined(nt:4G,ws:393|0|2.75,ac:sp) '
                 'AliApp(AP/10.1.90.9255) AlipayClient/10.1.90.9255 Language/zh-Hans '
                 'useStatusBar/true isConcaveScreen/true Region/CN MiniProgram NebulaX/1.0.0 Ariver/1.0.0-SNAPSHOT'
                 )

    def __init__(self, type_=3, customerId=786):
        if (type_ in (2, 3)):
            self.type_ = type_
        else:
            print("type_ 值错误！可选值：[2,3]")
            exit
        if (self.type_ == 2):
            self.name = "校内新闻"
        else:
            self.name = "通知公告"

        self.customerId = customerId
        self.session = requests.session()

        self.Referer = self.HOST + '/campus/campus/schoolinfo/list.action?type={type_}&_timestamp={timestamp}&customerId={customerId}'.format(
            type_=self.type_, timestamp=int(datetime.datetime.now().timestamp() * 1000), customerId=self.customerId)

    def get_ids(self, type_=None):
        headers = {
            'Origin': self.HOST,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': self.UserAgent,
            'Referer': self.Referer,
            'Accept-Language': 'zh-CN,en-US;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept-Encoding': 'gzip',
            'Content-Length': '44',
            'Host': 'www.17wanxiao.com',
            'Connection': 'Keep-Alive',
        }
        url = self.HOST + '/campus/campus/schoolinfo/load.action'

        data = {
            'customerId': self.customerId,  # 学校 ID,{784,869}
            'type': type_ if type_ else self.type_,  # {0,1} 学校简介,2 校内新闻,3 通知公告
            'pageSize': 1,  # 一页包含的条数
            'currPage': 1   # 当前页
        }
        response = self.session.post(url, headers=headers, data=data)
        if (response.status_code != 200):
            exit
        pages_res = response.json()
        data['pageSize'] = pages_res['totalCount'] + 1
        response = self.session.post(url, headers=headers, data=data)
        return response

    def get_pages(self, type_=None):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'X-Requested-With': 'com.eg.android.AlipayGphone',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.UserAgent,
            'Referer': self.Referer,
            'Accept-Language': 'zh-CN,en-US;q=0.9',
            'Accept-Encoding': 'gzip',
            'Host': 'www.17wanxiao.com',
            'Connection': 'Keep-Alive',
        }
        url = 'https://www.17wanxiao.com/campus/campus/schoolinfo/info.action'

        response = self.get_ids(type_)
        if (response.status_code != 200):
            exit
        pages_res = response.json()
        pages = pages_res['results']
        for page in pages:
            params = {'id': page['id']}
            response = self.session.get(
                url, headers=headers, timeout=5, params=params)
            if (response.status_code != 200):
                exit
            html = response.text
            title = re.search(r'<title>(.*)</title>', html).group(1)
            if title:
                page['title'] = title
            else:
                print("未匹配到标题！")

            body = re.search(r'<body>([\s\S]*)</body>', html).group(1)
            if body:
                page['body'] = body
                # print(body)
            else:
                print("未匹配到正文！")

            page['url'] = url + "?id=" + str(page['id'])

        return pages

    def get_school_info(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'X-Requested-With': 'com.eg.android.AlipayGphone',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.UserAgent,
            'Referer': self.Referer,
            'Accept-Language': 'zh-CN,en-US;q=0.9',
            'Accept-Encoding': 'gzip',
            'Host': 'www.17wanxiao.com',
            'Connection': 'Keep-Alive',
        }
        url = 'https://www.17wanxiao.com/campus/campus/schoolinfo/info.action'
        info = {}
        response = self.get_ids(type_=1)
        if (response.status_code != 200):
            exit
        response = response.json()
        info['name'] = response['results'][0]['title'][:-2]
        school_info_id = response['results'][0]['id']
        params = {'id': school_info_id}
        response = self.session.get(
            url, headers=headers, timeout=5, params=params)
        if (response.status_code != 200):
            exit
        html = response.text
        summary = re.search(r'<span[^>]*>(.*)</span>', html).group(1)
        # summary = re.findall('[\u4e00-\u9fa5、，。]+', summary)
        info['summary'] = summary
        return info

    def gen_feed(self):
        def _create_text_element(doc, type_, text, attribute=None):
            """Create a text element and return it."""
            element = doc.createElement(type_)
            element.appendChild(doc.createTextNode(text))
            if attribute:
                element.setAttribute(attribute['key'], attribute['vaule'])
            return element

        def _create_cdata_element(doc, type_, text, attribute=None):
            """Create a CDATA element and return it."""
            element = doc.createElement(type_)
            element.appendChild(doc.createCDATASection(text))
            if attribute:
                element.setAttribute(attribute['key'], attribute['vaule'])
            return element

        pages = self.get_pages()
        now = datetime.datetime.now()

        self._document = Document()

        # 头部
        rss_element = self._document.createElement('rss')
        rss_element.setAttribute('version', '2.0')
        rss_element.setAttribute('xmlns:atom', 'http://www.w3.org/2005/Atom')
        rss_element.setAttribute(
            'xmlns:dc', 'http://purl.org/dc/elements/1.1/')
        rss_element.setAttribute(
            'xmlns:content', 'http://purl.org/rss/1.0/modules/content/')
        self._document.appendChild(rss_element)

        # channel
        school_info = self.get_school_info()
        title = school_info['name'] + self.name
        link = 'https://www.17wanxiao.com/campus/campus/schoolinfo/list.action?type={type_}&customerId={customerId}'.format(
            type_=self.type_, customerId=self.customerId)

        self._channel = self._document.createElement('channel')
        rss_element.appendChild(self._channel)
        self._channel.appendChild(
            _create_text_element(self._document, type_='title', text=title))
        self._channel.appendChild(
            _create_text_element(self._document, type_='link',  text=link))
        self._channel.appendChild(
            _create_text_element(self._document, type_='description',  text=school_info['summary']))
        self._channel.appendChild(
            _create_text_element(self._document, type_='webMaster',  text="virgo_2333@163.com"))
        self._channel.appendChild(
            _create_text_element(self._document, type_='language',  text="zh-CN"))
        self._channel.appendChild(
            _create_text_element(self._document, type_='lastBuildDate',  text=now.strftime("%c")))

        for page in pages:
            if (page['createTime'].rfind('天前') == -1):
                date_time_list = re.findall(r'\d+', page['createTime'])

                mon = date_time_list[0]
                day = date_time_list[1]
                if (len(date_time_list) == 2):
                    hour = 0
                    minu = 0
                else:
                    hour = date_time_list[2]
                    minu = date_time_list[3]
            else:
                date_time = now + \
                    datetime.timedelta(
                        days=-int(re.search(r'\d', page['createTime']).group(0)))
                mon = date_time.month
                day = date_time.day
                hour = date_time.hour
                minu = date_time.minute

            pubDate = datetime.datetime(now.year, int(
                mon), int(day), int(hour), int(minu))
            content = re.sub(r'\s+', '', page['body'])

            # item
            self._item = self._document.createElement('item')
            self._channel.appendChild(self._item)
            self._item.appendChild(
                _create_text_element(self._document, type_='title',  text=page['title']))
            self._item.appendChild(
                _create_text_element(self._document, type_='link',  text=page['url']))
            self._item.appendChild(
                _create_cdata_element(self._document, type_='description',  text=page['summary']))
            self._item.appendChild(
                _create_text_element(self._document, type_='creator',  text=page['creator']))
            self._item.appendChild(
                _create_text_element(self._document, type_='categories',  text=self.name))
            self._item.appendChild(
                _create_text_element(self._document, type_='guid',  text=page['url'], attribute={'key': 'isPermaLink', 'vaule': 'false'}))
            self._item.appendChild(
                _create_text_element(self._document, type_='pubDate',  text=pubDate.strftime('%c')))
            self._item.appendChild(
                _create_cdata_element(self._document, type_='content:encoded', text=content))

        return self._document.toxml()
        # with open('t.xml', 'w') as f:
        #     self._document.writexml(f)


if __name__ == "__main__":
    t = SchoolFeed()
    s = t.gen_feed()
    pass
