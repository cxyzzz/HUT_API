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
条件所限，尚未明晰

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
`payProId` 随机生成一个整数即可
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
