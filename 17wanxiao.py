
import time
import datetime
import json
import logging
import requests

from login import CampusCard


def initLogging():
    logging.getLogger().setLevel(logging.INFO)
    logging.basicConfig(format="[%(levelname)s]; %(message)s")


class HealthyCheckIn(object):
    def __init__(self):
        self.lg_username = input()
        self.lg_password = input()
        self.sckey = input()
        self.check_url = "https://reportedh5.17wanxiao.com/sass/api/epmpics"
        initLogging()

    def get_post_json(self, token):
        jsons = {"businessType": "epmpics",
                 "jsonData": {"templateid": "pneumonia", "token": token},
                 "method": "userComeApp"}
        try:
            # 如果不请求一下这个地址，token就会失效
            requests.post("https://reportedh5.17wanxiao.com/api/clock/school/getUserInfo", data={'token': token})
            res = requests.post(url=self.check_url, json=jsons).json()
        except:
            return None
        if res['code'] != '10000':
            return None
        data = json.loads(res['data'])
        post_dict = {
            "areaStr": data['areaStr'],
            "deptStr": data['deptStr'],
            "deptid": data['deptStr']['deptid'],
            "customerid": data['customerid'],
            "userid": data['userid'],
            "username": data['username'],
            "stuNo": data['stuNo'],
            "phonenum": data['phonenum'],
            "templateid": data['templateid'],
            "updatainfo": [{"propertyname": i["propertyname"], "value": i["value"]} for i in
                           data['cusTemplateRelations']],
            "checkbox": [{"description": i["decription"], "value": i["value"]} for i in
                         data['cusTemplateRelations']],
        }
        # print(json.dumps(post_dict, sort_keys=True, indent=4, ensure_ascii=False))
        logging.info('获取完美校园打卡post参数成功')
        return post_dict

    def check_in(self):
        # 模拟登录获取token
        user_dict = CampusCard(self.lg_username, self.lg_password).user_info
        token = user_dict["sessionId"]
        if not user_dict['login']:
            return None
        # 获取post提交的字段
        post_dict = self.get_post_json(token)
        if not post_dict:
            logging.warning('获取完美校园打卡post参数失败')
            return None

        # post提交的json字段，根据自己的修改
        check_json = {"businessType": "epmpics", "method": "submitUpInfo",
                      "jsonData": {"deptStr": post_dict['deptStr'], "areaStr": post_dict['areaStr'],
                                   "reportdate": round(time.time() * 1000), "customerid": post_dict['customerid'],
                                   "deptid": post_dict['deptid'], "source": "app",
                                   "templateid": post_dict['templateid'], "stuNo": post_dict['stuNo'],
                                   "username": post_dict['username'], "phonenum": self.lg_username,
                                   "userid": post_dict['userid'], "updatainfo": post_dict['updatainfo'],
                                   "gpsType": 1, "token": token},
                      }
        response = requests.post(self.check_url, json=check_json)

        # 以json格式打印json字符串
        res = json.dumps(response.json(), sort_keys=True, indent=4, ensure_ascii=False)
        if response.json()['code'] != '10000':
            logging.warning(res)
        else:
            logging.info(res)

        # 拼接微信推送输出
        now_time = datetime.datetime.now()
        bj_time = now_time + datetime.timedelta(hours=8)
        test_day = datetime.datetime.strptime('2020-12-26 00:00:00', '%Y-%m-%d %H:%M:%S')
        post_msg = "\n".join([f"| {i['description']} | {i['value']} |" for i in post_dict['checkbox']])
        date = (test_day - bj_time).days
        self.server_push(f"""
------
#### 现在时间：
```
{bj_time.strftime("%Y-%m-%d %H:%M:%S %p")}
```
#### json字段：
```
{json.dumps(check_json, sort_keys=True, indent=4, ensure_ascii=False)}
```
#### 打卡信息：
------
| Text                           | Message |
| :----------------------------------- | :--- |
{post_msg}
------
```
{res}
```
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
        send_url = f"https://sc.ftqq.com/{self.sckey}.send"
        params = {
            "text": "健康打卡推送通知",
            "desp": desp
        }
        # 发送消息
        res = requests.post(send_url, data=params)
        # {"errno":0,"errmsg":"success","dataset":"done"}
        logging.info(res.text)
        if not res['errno']:
            logging.info('Server酱推送服务成功')
        else:
            logging.warning('Server酱推送服务失败')


if __name__ == '__main__':
    # HealthyCheckIn().check_in()
    HealthyCheckIn().server_push("")