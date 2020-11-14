import time
import datetime
import json
import requests

from login import CampusCard


class HealthyCheckIn(object):
    def __init__(self):
        self.lg_username = input()
        self.lg_password = input()
        self.address = input()
        self.addtext = input()
        self.code = input()
        self.emergency = input()
        self.emergencyPhone = input()
        self.sckey = input()

    def check_in(self):
        # 健康打卡的URL地址
        check_url = "https://reportedh5.17wanxiao.com/sass/api/epmpics"
        user_dict = CampusCard(self.lg_username, self.lg_password).get_user_school_info()
        area = {'address': self.address, 'text': self.addtext, 'code': self.code}
        areaStr = json.dumps(area, ensure_ascii=False)
        # POST提交的json字段，根据自己的修改
        check_json = {"businessType": "epmpics", "method": "submitUpInfo",
                      "jsonData": {"deptStr": {"deptid": user_dict['deptid'], "text": user_dict['text']},
                                   "areaStr": areaStr,
                                   "reportdate": round(time.time() * 1000), "customerid": "1999",
                                   "deptid": user_dict['deptid'],
                                   "source": "app",
                                   "templateid": "pneumonia", "stuNo": user_dict['stuNo'],
                                   "username": user_dict['username'], "phonenum": self.lg_username,
                                   "userid": user_dict['userid'],
                                   "updatainfo": [{"propertyname": "bodyzk", "value": "正常温度(小于37.3)"},
                                                  {"propertyname": "istouchcb", "value": "在校（含当日在校内居住）"},
                                                  {"propertyname": "sfwz2", "value": "内地学生"},
                                                  {"propertyname": "symptom", "value": "无"},
                                                  {"propertyname": "homehealth", "value": "无"},
                                                  {"propertyname": "isConfirmed", "value": "无"},
                                                  {"propertyname": "ownbodyzk", "value": "良好"},
                                                  {"propertyname": "ishborwh", "value": "无"},
                                                  {"propertyname": "outdoor", "value": "绿色"},
                                                  {"propertyname": "ownPhone", "value": self.lg_username},
                                                  {"propertyname": "emergencyContact", "value": self.emergency},
                                                  {"propertyname": "mergencyPeoplePhone",
                                                   "value": self.emergencyPhone}
                                                  ],
                                   "gpsType": 0,
                                   "token": user_dict['token']},
                      }
        response = requests.post(check_url, json=check_json)
        # 以json格式打印json字符串
        res = json.dumps(response.json(), sort_keys=True, indent=4, ensure_ascii=False)

        print(res)

        # 拼接微信推送输出
        now_time = datetime.datetime.now()
        bj_time = now_time + datetime.timedelta(hours=8)
        test_day = datetime.datetime.strptime('2020-12-26 00:00:00', '%Y-%m-%d %H:%M:%S')
        date = (test_day - bj_time).days
        self.server_push(f"""
------
### 现在时间：
```
{bj_time.strftime("%Y-%m-%d %H:%M:%S %p")}
```
### 打卡信息：
------
| Text                           | Message |
| :----------------------------------- | ---: |
| 专业/部门                            | {user_dict['text']} |
| 姓名                                 | {user_dict['username']}  |
| 学号                                 |  {user_dict['stuNo']}   |
| 当前位置                             |   {self.address}   |
| 今日体温                             |   正常温度(小于37.3)   |
| 自己当日所在位置                     |   在校（含当日在校内居住）   |
| 身份类别                             |   内地学生   |
| 是否出现可以症状                     |   无   |
| 是否存在高危行为                      |    无  |
| 被要求采取医学措施                    |   无   |
| 家庭成员身体状况                      |   良好   |
| 所在小区是否有疫情                   |   无   |
| 居民健康码颜色                       |   绿色   |
| 本人电话                             |  {self.lg_username}    |
| 紧急联系人姓名                       |    {self.emergency}  |
| 紧急联系人电话                       |  {self.emergencyPhone}    |
------
```
{res}
```
> 关于打卡信息
>
> 1、成功则打卡成功
>
> 2、系统异常则是打卡频繁

### ⚡考研倒计时:
```
{date}天
```

>
> [GitHub项目地址](https://github.com/ReaJason/17wanxiaoCheckin-Actions) 
>
>期待你给项目的star✨
""")

    def server_push(self, desp):
        SCKEY = self.sckey
        headers = {"Content-type": "application/x-www-form-urlencoded; charset=UTF-8"}
        send_url = f"https://sc.ftqq.com/{SCKEY}.send"
        params = {
            "text": "完美校园健康打卡推送通知",
            "desp": desp
        }
        # 发送消息
        response = requests.post(send_url, data=params, headers=headers)
        if response.json()["errmsg"] == 'success':
            print("Server酱推送服务成功")
        else:
            print("Server酱推送服务失败")


if __name__ == '__main__':
    HealthyCheckIn().check_in()


