import datetime
import re
import requests
from xml.dom.minidom import Document
if __name__ == "__main__":
    from HUT import JobCalendar
else:
    from app.HUT import JobCalendar


class Feed(object):
    def __init__(self):
        super().__init__()
        self._document = Document()

    def _create_text_element(self, type_, text='', attribute=None):
        """Create a text element and return it."""
        element = self._document.createElement(type_)
        element.appendChild(self._document.createTextNode(text))
        if attribute:
            for _attribute in attribute:
                element.setAttribute(_attribute['key'], _attribute['vaule'])
        return element

    def _create_cdata_element(self, type_, text='', attribute=None):
        """Create a CDATA element and return it."""
        element = self._document.createElement(type_)
        element.appendChild(self._document.createCDATASection(text))
        if attribute:
            for _attribute in attribute:
                element.setAttribute(_attribute['key'], _attribute['vaule'])
        return element

    def _create_item(self, title, link, guid, pubDate, description='', creator='', categories='', content=''):
        self._item = self._document.createElement('item')
        self._item.appendChild(
            self._create_text_element(type_='title',  text=title))
        self._item.appendChild(
            self._create_text_element(type_='link',  text=link))
        self._item.appendChild(
            self._create_cdata_element(type_='description',  text=description))
        self._item.appendChild(
            self._create_text_element(type_='creator',  text=creator))
        self._item.appendChild(
            self._create_text_element(type_='categories',  text=categories))
        self._item.appendChild(
            self._create_text_element(type_='guid',  text=link, attribute=[{'key': 'isPermaLink', 'vaule': 'false'}]))
        self._item.appendChild(
            self._create_text_element(type_='pubDate',  text=pubDate))
        self._item.appendChild(
            self._create_cdata_element(type_='content:encoded', text=content))
        return self._item

    def _create_channel(self, title, link='', description='', webMaster='', language='zh-CN', lastBuildDate='', items=[]):
        self._channel = self._document.createElement('channel')
        self._channel.appendChild(
            self._create_text_element(type_='title', text=title))
        self._channel.appendChild(
            self._create_text_element(type_='link',  text=link))
        self._channel.appendChild(
            self._create_text_element(type_='description',  text=description))
        self._channel.appendChild(
            self._create_text_element(type_='webMaster',  text=webMaster))
        self._channel.appendChild(
            self._create_text_element(type_='language',  text="zh-CN"))
        self._channel.appendChild(
            self._create_text_element(type_='lastBuildDate', text=lastBuildDate))

        for item in items:
            self._channel.appendChild(item)

        return self._channel


class SchoolFeed(Feed):
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
        super().__init__()
        if (type_ in (2, 3)):
            self.type_ = type_
        else:
            print("type_ 值错误！可选值：[2,3]")
            exit
        if (self.type_ == 2):
            self.name = "校内新闻"
        else:
            self.name = "通知公告"
        # print(self.type_, type_, self.name)
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
            'pageSize': 1,  # 一页包含的数据条数
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
        pages = self.get_pages()
        now = datetime.datetime.now()

        # 头部
        attribute = []
        attribute.append({'key': 'version', 'vaule': '2.0'})
        attribute.append(
            {'key': 'xmlns:atom', 'vaule': 'http://www.w3.org/2005/Atom'})
        attribute.append(
            {'key': 'xmlns:dc', 'vaule': 'http://purl.org/dc/elements/1.1/'})
        attribute.append(
            {'key': 'xmlns:content', 'vaule': 'http://purl.org/rss/1.0/modules/content/'})
        rss_element = self._create_text_element(
            type_='rss', attribute=attribute)
        self._document.appendChild(rss_element)

        # channel
        school_info = self.get_school_info()
        channel_title = school_info['name'] + self.name
        channel_description = school_info['summary']
        channel_lastBuildDate = now.strftime("%c")
        channel_webMaster = 'virgo_2333@163.com'
        channel_link = 'https://www.17wanxiao.com/campus/campus/schoolinfo/list.action?type={type_}&customerId={customerId}'.format(
            type_=self.type_, customerId=self.customerId)

        Items = []
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

            # item
            item_title = page['title']
            item_link = page['url']
            item_description = page['summary']
            item_creator = page['creator']
            item_categories = self.name
            item_guid = page['url']
            item_pubDate = datetime.datetime(now.year, int(
                mon), int(day), int(hour), int(minu)).strftime('%c')
            item_content = re.sub(r'\s+', '', page['body'])
            self._item = self._create_item(
                title=item_title, link=item_link, guid=item_guid, pubDate=item_pubDate,
                description=item_description, creator=item_creator, categories=item_categories, content=item_content)
            Items.append(self._item)
        self._channel = self._create_channel(
            title=channel_title, link=channel_link, description=channel_description,
            webMaster=channel_webMaster, lastBuildDate=channel_lastBuildDate, items=Items)
        rss_element.appendChild(self._channel)

        with open(self.name + '_feed.xml', 'w') as f:
            self._document.writexml(f)

        return self._document.toxml()


class JobFeed(Feed):
    def __init__(self, **kwargs):
        super().__init__()
        self.job = JobCalendar(**kwargs)

    def gen_feed(self):

        # 头部
        attribute = []
        attribute.append({'key': 'version', 'vaule': '2.0'})
        attribute.append(
            {'key': 'xmlns:atom', 'vaule': 'http://www.w3.org/2005/Atom'})
        attribute.append(
            {'key': 'xmlns:dc', 'vaule': 'http://purl.org/dc/elements/1.1/'})
        attribute.append(
            {'key': 'xmlns:content', 'vaule': 'http://purl.org/rss/1.0/modules/content/'})
        rss_element = self._create_text_element(
            type_='rss', attribute=attribute)
        self._document.appendChild(rss_element)

        # channel
        now = datetime.datetime.now()
        channel_title = self.job.SCHOOL_LIST[self.job.school]
        if (self.job.mode == 'getonlines'):
            flag = 1  # 区分在线招聘和岗位招聘，方便后面生成item
            channel_title += '在线招聘'
            item_link = self.job.ONLINE_URL
        elif (self.job.mode == 'getjobs'):
            flag = 0
            channel_title += '岗位招聘'
            item_link = self.job.JOB_URL
        channel_lastBuildDate = now.strftime("%c")
        channel_webMaster = 'virgo_2333@163.com'
        channel_link = 'http://{0}/module/{1}'.format(
            self.job.HOST, self.job.mode[3:])

        Items = []
        datas = self.job.get_datas()
        for data in datas:
            # item
            item_title = data['title'] if flag else '{0}-{1}'.format(data['job_name'], '-' + data['company_name'])
            item_link += (data['recruitment_id'] if flag else data['publish_id'])
            item_description = data['job_recruitment'] if flag else '{0} {1} {2}\n{3}{4}\n{5}\n时间：{6}至{7}'.format(
                data['city_name'], data['salary'], data['scale'], data['degree_require'], data['about_major'], data['keywords'], data['publish_time'], data['end_time'])
            item_creator = data['company_name']
            item_categories = data['recruit_type'] if flag else data['industry_category']
            item_guid = data['recruitment_id'] if flag else data['publish_id']
            item_pubDate = data['create_time'] if flag else data['publish_time']
            item_content = data['content']
            self._item = self._create_item(
                title=item_title, link=item_link, guid=item_guid, pubDate=item_pubDate,
                description=item_description, creator=item_creator, categories=item_categories, content=item_content)
            Items.append(self._item)
        self._channel = self._create_channel(
            title=channel_title, link=channel_link, description=channel_title,
            webMaster=channel_webMaster, lastBuildDate=channel_lastBuildDate, items=Items)
        rss_element.appendChild(self._channel)

        with open(channel_title + '_feed.xml', 'w') as f:
            self._document.writexml(f)

        return self._document.toxml()


if __name__ == "__main__":
    s = JobFeed(mode='getjobs', style='full')
    t = s.gen_feed()
    # s = SchoolFeed()
    # t = s.gen_feed()
    pass
