# 🐱‍🏍17wanxiaoCheckin-Actions

> 基于Github-Actions的完美校园健康打卡

⚡因需要会手机抓包基础才能实现（后期有时间再写），所以该项目只作为一个actions的效果展示和项目搭建

### Actions具体流程

<!--tips：actions配置文件在\.github\workflows\run.yml中-->

#### 0 参数设置(secret)

```python
# 设置如下secret字段
"""
TEXT(学院专业班级信息)
ADDRESS(详细地址)
ADDTEXT(省-市-县/区)
DEPTID(未知id字段)
USERID(完美校园分配的用户id)
STUNUM(学号)
USERNAME(姓名)
PHONENUM(电话)
EMERGENCY(紧急联系人)
EMERGENCYPHONE(紧急联系人电话)
"""
```

#### 1 计划时间参数

```python
schedule:
   - cron: 0 22 * * * # 表示每天6点进行任务
# cron后面的时间为国际事件
# 五位数(空格分隔)分别为分钟、小时、天、月、一个星期的第几天
# 国际时与北京时的查询网站：http://www.timebie.com/cn/universalbeijing.php
```

#### 2 Install Python

```python
# 为虚拟机安装python3环境
run: |
    sudo apt update && \
    sudo apt install python3
# 由于使用的是Ubuntu的虚拟机，因此执行的是linux语句
```

#### 3 requirements

```python
# 为py程序的执行安装第三方库requests
run: |
    pip3 install -r requirements.txt
```

#### 4 Checkin

```python
# 运行py脚本文件
run: |
    python3 17wanxiao.py
```

```python
# json字段需要通过手机抓包健康打卡获取(能力有限，暂无其他办法)
import requests

base_url = "https://reportedh5.17wanxiao.com/sass/api/epmpics"

json = {"businessType": "epmpics", "method": "submitUpInfo",
        "jsonData": {"deptStr": {"deptid": {}, "text": "{学院-专业-班级}"},
                     "areaStr": "{地址}",
                     "reportdate": {时间戳*1000}, "customerid": "1999", "deptid": {}, "source": "alipay",
                     "templateid": "pneumonia", "stuNo": "{学号}", "username": "{姓名}", "phonenum": "{电话号码}",
                     "userid": "{独一无二的字段}", "updatainfo": [{"propertyname": "bodyzk", "value": "正常温度(小于37.3)"},
                                                          {"propertyname": "istouchcb", "value": "自己家中"},
                                                          {"propertyname": "sfwz2", "value": "内地学生"},
                                                          {"propertyname": "symptom", "value": "无"},
                                                          {"propertyname": "homehealth", "value": "无"},
                                                          {"propertyname": "isConfirmed", "value": "无"},
                                                          {"propertyname": "ownbodyzk", "value": "良好"},
                                                          {"propertyname": "ishborwh", "value": "无"},
                                                          {"propertyname": "outdoor", "value": "绿色"},
                                                          {"propertyname": "isContactFriendIn14", "value": "没有"},
                                                          {"propertyname": "ownPhone", "value": "{联系电话}"},
                                                          {"propertyname": "emergencyContact", "value": "{紧急联系人}"},
                                                          {"propertyname": "mergencyPeoplePhone",
                                                           "value": "{紧急联系人电话}"}], "gpsType": 1}}

response = requests.post(base_url, json=json)
res = response.text
print(res)
```

#### 5 成功截图

![成功截图](https://s1.ax1x.com/2020/07/01/NomfVH.png)

