# HUT-API

## HUT 强智教务系统 API  

参考 <https://github.com/TLingC/QZAPI>

### API列表

#### authUser

登录帐号  
`http://218.75.197.123:83/app.do?method=authUser&xh=学号&pwd=密码`

**返回值**  
返回 JSON 对象

>success: 登录状态  
token: Token  
scsj: 未知  
sjyzm: 未知  
useraccount: 登录用户  
usertype: 用户类型，学生为 2  
userdwmc: 学院  
username: 用户姓名  
userpasswd: 用户密码  
userrealname: 用户姓名

之后的查询均需携带 Token

#### getStudentIdInfo

~~获取学号信息(已禁止查询)  
`http://218.75.197.123:83/app.do?method=getStudentIdInfo&xh=#学号#`~~

**返回值**  
返回 JSON 对象

>bjid：未知  
ndzyid：未知  
yxid：未知  
xxdm：未知

#### getCurrentTime

获取当前时间、周次、学年等信息  
`http://218.75.197.123:83/app.do?method=getCurrentTime&currDate=#查询日期#`

**返回值**  
返回 JSON 对象

>e_time: 周结束时间  
s_time: 周开始时间  
xnxqh: 学年  
zc: 周次

#### getKbcxAzc

获取课程表  
`http://218.75.197.123:83/app.do?method=getKbcxAzc&xh=#学号#&xnxqid=#学年#&zc=#周次#`

**返回值**  
返回JSON数组

>jsmc: 教室名称  
jssj: 下课时间  
jsxm: 教师姓名  
kcmc: 课程名称  
kkzc: 课程教学周  
kcsj: 课程时间（eg: 50304 表示星期五第3-4节）  
kssj: 上课时间  
sjbz: 未知

#### getXqcx

获取校区  
`http://218.75.197.123:83/app.do?method=getXqcx`

**返回值**  
返回JSON数组

>xqid: 校区 iD  
xqmc: 校区名称  

#### getJxlcx

获取校区教学楼信息  
`http://218.75.197.123:83/app.do?method=getJxlcx&xqid=#校区ID#`

**返回值**  
返回JSON数组

>jzwid: 教学楼 ID  
jzwmc: 教学楼名称

#### getKxJscx

获取空教室  
`http://218.75.197.123:83/app.do?method=getKxJscx&time=#查询日期#&idleTime=#见下方说明#&xqid=#校区ID#&jxlid=#教学楼ID#&classroomNumber=_#可容纳人数，见下方说明#`

xqid(校区 ID)、jxlid(教学楼 ID)、classroomNumber(教室容纳人数)是可选参数

**idleTime取值**  
> allday：全天  
am：上午  
pm：下午  
night：晚上

**classroomNumber**  
> 30：30人以下  
30-40：30-40人  
40-50：40-50人  
60：60人以上

**返回值**  
返回JSON数组

>jsh: 未知  
jsid: 教室 ID  
jsmc: 教室名称  
jzwid: 所在楼ID  
jzwmc: 教学楼名称  
xqmc: 校区名称  
yxzws: 教室容量  
zws: 未知，和yxzws相同  
jxl: 教学楼  
success: 状态  
xnxqid: 学年  

#### getUserInfo

获取帐号信息  
`http://218.75.197.123:83/app.do?method=getUserInfo&xh=#学号#`

**返回值**  
返回 JSON 对象

>bj: 班级  
dh: 电话  
dqszj: 未知，与入学年份、年级相同  
email: 电子邮箱  
fxzy: 辅修专业  
ksh: 高考考号  
nj: 年级  
qq: QQ 号  
rxnf: 入学年份  
usertype: 用户类别，学生为 2  
xb: 性别  
xh: 学号  
xm: 姓名  
xz: 未知  
yxmc：院系名称  
zymc：专业名称

#### getXnxq

获取学年和学期信息  
`http://218.75.197.123:83/app.do?method=getXnxq&xh=#学号#`

**返回值**  
返回JSON数组

>isdqxq: 是否为当前学期，1 为是，0 为否  
xnxq01id: 学年id  
xqmc: 学年名称  

#### getCjcx

获取成绩信息  
`http://218.75.197.123:83/app.do?method=getCjcx&xh=#学号#&xnxqid=#学期学年ID#`

**返回值**  
返回 JSON 数组

>bz: 未知  
cjbsmc: 未知  
kclbmc: 课程类别名称  
kcmc: 课程名称  
kcxzmc: 课程性质名称  
kcywmc: 未知  
ksxzmc: 考试性质名称  
xf: 学分  
xm: 姓名  
xqmc: 学期名称  
zcj: 总成绩  
success: 状态  

#### getKscx

获取考试信息  
`http://218.75.197.123:83/app.do?method=getKscx&xh=#学号#`

**返回值**  
返回 json 对象
>bj: 班级  
bz: 未知  
jsmc: 教室名称  
kcmc: 课程名称  
ksjc: 考试节次  
ksmc: 考试名称  
ksqssj: 考试时间日期  
xm: 姓名

#### getEarlyWarnInfo

获取学籍预警信息  
`http://218.75.197.123:83/app.do?method=getEarlyWarnInfo&xh=#学号#&history=#见下方说明#`

**history取值**  
> 0：当前预警  
1：历史预警

**返回值**  
条件所限，尚未明晰

### Python 示例

#### 安装

1. 使用 pip  
`pip install -r requerments.txt`

2. 使用 [pipenv](https://docs.pipenv.org)  
`pipenv install`

#### 使用

1,2任选一个

1. 使用环境变量 (推荐)  
`export ACCOUNT=#你的学号#`
`export PASSWORD=#密码#`

2. 修改文件中的`account = os.getenv('ACCOUNT') password = os.getenv('PASSWORD')` 把等于号后面的替换为你的学号以及密码

#### 功能

1. 支持导出课表为 ics 日历文件

2. WEB 展示(不会前端，暂未完善)
![Screenshot_20190910_212948.png](https://i.loli.net/2019/09/10/Ns3qxcToGBQblIv.png)

## 电费查询

### getJzinfo

`http://h5cloud.17wanxiao.com:8080/CloudPayment/user/getRoom.do?payProId=#支付订单ID#&schoolcode=#学校代码#&optype=#状态码#&areaid=#校区ID#&buildid=#楼栋ID#&unitid=#单元ID#&levelid=#等级ID#&businesstype=#业务类型#`

以下查询中不变的值：
`payProId` 随机生成一个大于1000的整数即可
`schoolcode` 为学校代码，请自行查询
`businesstype=2`

#### 获取校区信息

>optype=1  
arieaid=0  
buildid=0  
unitid=0  
levelid=0  

#### 获取楼栋信息

>optype=2  
areaid=#从前面获取到的校区信息中查找#  
buildid=0  
unitid=0  
levelid=0  

#### 获取寝室信息

>optype=4  
areaid=#从前面获取到的校区信息中查找#  
buildid=#从前面获取到的楼栋信息中查找#  
unitid=0  
levelid=-1  

### 查询电费

`http://h5cloud.17wanxiao.com:8080/CloudPayment/user/getRoomState.do?payProId=#订单ID#&schoolcode=#学校ID#&businesstype=#业务类型#&roomverify=#寝室编号#`

>payProId 随机生成一个整数即可  
schoolcode 为学校代码，请自行查询  
businesstype=2  
roomverify #从前面获取到的寝室信息中查找#

## 就业中心 API

带 * 号的为可选参数，请求时可不带此关键字

### 宣讲会

#### 宣讲会日程

`http://job.hut.edu.cn/module/getcareers?start=#起始点#&count=#个数#&k=#企业名称关键字#&address=#地址#&professionals=#专业#&career_type=#类型#&type=#区域#&day=#日期#`

>start: 起始点，即从第几个开始显示  
count: 从 start 开始，显示 count 个数据  
*k: 企业名称关键字，空为所有(也可使用 keyword 关键字)  
*address： 企业地址
*professionals: 专业，空为所有  
*career_type: 类型，可选值：{实习、校招、包含实习，空为全部}  
type: 范围，可选值：{校内：inner，校外：outer}  
day: 日期：eg:2019-10-23,空为当前日期  

返回 json 对象
<details>
``` json
{
    "code":状态码,
    "msg":"信息",
    "data":[{
        "overdue":"1",
        "is_yun":"0",
        "career_state":"企业状态",
        "sort_time":"170774",
        "career_talk_id":"255337",
        "company_id":"公司 ID",
        "company_name":"公司名称",
        "logo":"公司 LOGO 地址",
        "hotcount":"4",
        "professionals":"需求专业",
        "career_type":"",
        "recruit_type":"",
        "company_review":"",
        "company_property":"公司属性","industry_category":"行业类别",
        "city_name":"城市名称",
        "meet_name":"会议名称（公司名称）",
        "meet_time":"时间",
        "school_name":"",
        "address":"地点",
        "room":"",
        "view_count":"访问统计",
        "is_above_college_degree":"是否要求大学以上学历",
        "is_above_bachelor_degree":"是否要求本科以上学历",
        "is_above_master_degree":"是否要求硕士以上学历",
        "is_above_doctor_degree":"是否要求博士以上学历",
        "is_recommend":"是否推荐",
        "recommend_time":"推荐时间",
        "meet_day":"日期"
    }]
}
```
</details>

#### 企业详细信息页面

`http://static.bibibi.net/student/chance/preachmeetingdetails.html?token=yxqqnn0000000012&career_id=#企业 ID#`

>career_id: 可从前面宣讲会返回值中获取

#### 企业详细信息 API

`http://student.bibibi.net/index.php?r=career/ajaxgetcareerdetail&token=yxqqnn0000000012&career_id=#企业 ID#`

>career_id: 可从前面宣讲会返回值中获取

返回 json 对象

<details>
``` json
{
    "code":状态码,
    "msg":"信息",
    "data":{
        "company_id":公司 ID,
        "career_talk_id":293513,
        "remark":"备注(包含企业详细信息及职位详情，HTML 格式)",
        "school_name":"学校名称",
        "meet_name":"会议名称（企业名称）",
        "meet_time":"日期 时间",
        "address":"地址",
        "room":"",
        "map_lat":维度,
        "map_lng":经度,
        "map_address":"地图地址",
        "sign_up_type":0,
        "sign_up_limit":0,
        "sign_up_end_time":"",
        "career_state":0,
        "is_yun":0,
        "yun_live_url":"",
        "yun_vod_url":"",
        "view_count":访问统计,
        "book_state":"已同意",
        "for_faculty":"",
        "company_name":"公司名称",
        "is_overdue":false,
        "is_limit":false,
        "sign_up_count":0,
        "is_sign_up":false,
        "qr_code":"",
        "company":{
            "company_id":公司 ID,
            "company_name":"公司名称",
            "short_name":null,
            "keywords":null,
            "logo_url":"公司 LOGO 地址",
            "industry_category":"行业类别",
            "company_property":公司属性,
            "scale":"规模","registered_capital":null,
            "apply_url":null,
            "url":null,
            "review":null,
            "introduction":"公司介绍",
            "label":null,
            "stock_code":null,
            "mobile":null,
            "job_mobile":null,
            "tel":"电话",
            "mail":"邮箱",
            "job_mail":"工作邮箱",
            "video_url":"",
            "identification_pics":null,
            "scene_pics":null,
            "hr":null,
            "province":null,
            "city_name":"城市名称",
            "hotcount":0,
            "source":null,
            "verification_code":null,
            "send_time":null,"recent_career_talk_time":null,
            "career_talk_qty":null,
            "job_qty":null,
            "practice_qty":null,
            "invite_qr_img":null,
            "view_count":null,
            "address":"公司地址",
            "post_code":null,
            "is_yy_view":null,
            "source_school_id":null,
            "source_school":null,
            "h5_url":null,
            "company_no":null,
            "org_code":null,
            "password":null,
            "openid":null,
            "pre_company_name":null,
            "province_area":null,
            "area_name":null,
            "is_sync":null,
            "state":"状态",
            "no_pass":null,
            "approve_by":null,
            "approve_time":null,
            "create_by":null,
            "create_time":null,
            "is_disable":0,
            "modify_by":null,
            "modify_time":null,
            "m_company_id":null,
            "is_auth":null,
            "recruit_remark":null,
            "last_login_time":null,
            "last_recruit_time":null,
            "last_deduct_time":null,
            "old_company_id":null
            },
        "is_fav":0,
        "hr":{
            "nick_name":null,
            "logo_url":null},
        "docs":[],
        "practices":[],
        "jobs":[{
                "publish_id":发布 ID,
                "job_name":"岗位名称",
                "about_major":"相关专业",
                "job_number":"5",
                "city_name":"城市名称",
                "degree_require":"学历要求",
                "salary":"工资",
                "create_time":"创建时间"
            }],
        "school_id":学校 ID,
        "notice":"通知(HTML 格式)",
        "is_auth":0,
        "is_sign_in":false,
        "credit_info":{
            "credit_id":信用 ID,
            "company_id":公司 ID,
            "info_integrity_grade":"资料完整度等级",
            "info_integrity_score":资料得分,
            "recruit_liveness_grade":"招聘活跃度等级",
            "recruit_liveness_score":招聘活跃度得分,
            "income_audit_grade":"高校审核等级",
            "income_audit_cnt":高校审核,
            "complaint_cnt":0,
            "total_score":总得分,
            "ranking":0,
            "update_time":"更新时间",
            "percent_beat":100
        },
        "user_info":{
            "student_id":-1,
            "student_key":""
            },
        "bars":[],
        "moocs": 广告
}
```
</details>

#### 岗位详细信息页面

`http://static.bibibi.net/student/chance/newestjobdetails.html?token=yxqqnn0000000012&publish_id=#发布 ID#`

>publish_id: 可从前面企业详细信息 API 返回值中获取

#### 岗位详细信息 API

`http://student.bibibi.net/index.php?r=job/ajaxgetjobdetail&token=yxqqnn0000000012&publish_id=#发布 ID#`

>publish_id: 可从前面企业详细信息 API 返回值中获取

返回 json 对象
<details>
``` json
{
    "code":1,
    "msg":"",
    "data":{
        "publish_id":发布 ID,
        "job_name":"岗位名称",
        "about_major":"相关专业",
        "job_number":"5",
        "city_name":"城市名称",
        "degree_require":"学历要求",
        "salary":"工资",
        "create_time":"创建时间",
        "keywords":"关键字",
        "is_practice":0,
        "publish_hr_openid":"",
        "job_descript":"岗位介绍",
        "category":"类别",
        "welfare":"福利",
        "job_require":"",
        "view_count":访问统计,
        "job_other":"",
        "intro_apply":"简历投递方式",
        "work_address":null,
        "job_status":"岗位状态",
        "publish_time":"2019年10月14日",
        "end_time":"2020年10月21日",
        "time_type":"","amount_welfare_min":null,
        "amount_welfare_max":null,
        "source":"oper",
        "company":{
            "company_id":公司 ID,
            "company_name":"公司名称",
            "logo_url":"公司 LOGO 地址",
            "industry_category":"行业类别",
            "scale":"规模",
            "apply_url":null,
            "review":null,
            "introduction":"公司介绍",
            "job_mail":"工作邮箱",
            "video_url":"",
            "city_name":"城市名称",
            "hotcount":0,
            "address":"公司地址",
            "state":"状态",
            "is_disable":0,
            "scene_pics":null
        },
        "is_apply":0,
        "apply_cnt":"0",
        "school_list":[],
        "is_subscribe":0,
        "credit_info":{
            "credit_id":信用 ID,
            "company_id":公司 ID,
            "info_integrity_grade":"资料完整度等级",
            "info_integrity_score":资料得分,
            "recruit_liveness_grade":"招聘活跃度等级",
            "recruit_liveness_score":招聘活跃度得分,
            "income_audit_grade":"高校审核等级",
            "income_audit_cnt":高校审核,
            "complaint_cnt":0,
            "total_score":总得分,
            "ranking":0,
            "update_time":"更新时间",
            "percent_beat":100
        },
    "user_info":{
        "student_key":""
        },
    "moocs":广告,
    "is_fav":0
    }
}
```
</details>

#### 企业信用信息页面

`http://static.bibibi.net/student/chance/company_credit.html?token=yxqqnn0000000012&company_id=#公司 ID#`

>company_id: 可从前面企业详细信息 API 返回值中获取

#### 企业信用信息 API

`http://student.bibibi.net/index.php?r=complaint/ajax_company_complaint_info&token=yxqqnn0000000012&company_id=#公司 ID#`

>company_id: 可从前面企业详细信息 API 返回值中获取

### 双选会

#### 双选会日程

`http://job.hut.edu.cn/module/getjobfairs?start=#起始点#&count=#个数#&type=#区域#&address=#地址#&organisers=#主办方#&keyword=#企业名称关键字#&day=#日期#`

>start: 同宣讲会  
count: 同宣讲会  
*type: 同宣讲会  
*address: 同宣讲会  
*organisers: 组织者
*keyword: 企业名称关键字，空为所有(也可使用 k 关键字)  
*day: 范围，默认为校内，任意值为校外

返回 json 对象

<details>
``` json
{
    "code":状态码,
    "msg":"信息",
    "data":[{
        "overdue":"1",
        "sort_time":"53005",
        "fair_id":"4126",
        "inner_school":"0",
        "type":"0",
        "is_online":"0",
        "title":"标题",
        "organisers":"组织者",
        "school_name":"学校名称",
        "address":"地址",
        "fact_c_count":"283",
        "plan_c_count":"500",
        "view_count":"访问统计",
        "meet_time":"时间",
        "is_recommend":"是否推荐",
        "recommend_time":"推荐时间",
        "is_inner":"0",
        "is_over":false,
        "meet_day":"日期",
        "school_cnt":"181",
        "internet_cnt":"78",
        "total":259
    }]
}
```
</details>

#### 双选会详细信息页面

`http://job.hut.edu.cn/detail/jobfair?id=#ID#`

>id: 可从前面返回值中 fair_id 获取

#### 双选会详细信息 API

`https://s.bysjy.com.cn/index.php?r=chance/ajaxgetjobfairdetail&token=yxqqnn0000000012&fair_id=`

>fair_id: 可从前面返回值中获取

返回 json 对象

<details>
``` json
{
    "code":状态码,
    "msg":"信息",
    "data":{
        "fair_id":双选会 ID,
        "school_id":学校 ID,
        "type":0,
        "title":"标题",
        "organisers":"组织者",
        "school_name":"学校名称",
        "is_outer":0,
        "is_show_company":1,
        "is_online":0,
        "address":"地址",
        "content":"内容(HTML 格式)",
        "scene_pics":"",
        "professionals":"","recruit_notices":"通知(HTML 格式)",
        "company_signup_type":"招聘信息报名",
        "map_address":"",
        "map_lat":0,
        "map_lng":0,
        "is_need_ticket":0,
        "is_need_deposit":0,
        "view_count":访问统计,
        "meet_time":"时间",
        "is_overdue":false,
        "ticket":null,
        "is_fav":0,
        "docs":[],
        "companies":[],
        "is_auth":0,
        "job_list":[],
        "is_arbeitsagentur_jobfair":0
    }
}
```
</details>

### 效果图

![IMG_20191023_220926.jpg](https://i.loli.net/2019/10/23/YEznJiaecbr4PTV.jpg)
