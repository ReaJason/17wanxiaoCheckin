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
        self.score_url = 'https://server.59wanmei.com/YKT_Interface/score'
        self.sign_url = 'https://server.59wanmei.com/YKT_Interface/xyk'
        initLogging()
        self.get_token()

    def get_token(self):
        user_dict = CampusCard(self.lg_username, self.lg_password).user_info
        if not user_dict['login']:
            return None
        self.token = user_dict["sessionId"]

    def get_post_json(self):
        jsons = {"businessType": "epmpics",
                 "jsonData": {"templateid": "pneumonia", "token": self.token},
                 "method": "userComeApp"}
        try:
            # 如果不请求一下这个地址，token就会失效
            requests.post("https://reportedh5.17wanxiao.com/api/clock/school/getUserInfo", data={'token': self.token})
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

    def get_score(self):
        payload = 'token={}&method={}&param=%7B%22token%22%3A%22{}%22%7D'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; Redmi K20 Pro Premium Edition Build/QKQ1.190825.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.198 Mobile Safari/537.36 Wanxiao/5.3.1',

        }
        # {"circleExpire":72,"opCircleList":[],"signCircleStatus":{"title":"签到","foodCoupon":1,"status":0},"activeCircleList":[{"modifyTime":1599352663000,"id":934055,"title":"活跃奖励","foodCoupon":1}],"code_":0,"activeCircleTime":1,"result_":true,"circleList":[],"message_":"操作成功"}
        # {"circleExpire":72,"opCircleList":[],"signCircleStatus":{"title":"签到","foodCoupon":2,"status":1},"activeCircleList":[{"modifyTime":1605683321000,"id":934055,"title":"活跃奖励","foodCoupon":1}],"code_":0,"activeCircleTime":1,"result_":true,"circleList":[],"message_":"操作成功"}
        score_circle_list_res = requests.post(self.score_url, data=payload.format(self.token, 'gainScoreCircleList', self.token), headers=headers)

        # 每日签到
        daily_msg = "每日签到："
        if not score_circle_list_res.json()['signCircleStatus']['status']:
            sign_score = score_circle_list_res.json()['signCircleStatus']['foodCoupon']
            try:
                sign_res = requests.post(self.sign_url, data=payload.format(self.token, "WX_h5signIn", self.token), headers=headers)
                if sign_res.json()['result_']:
                    msg = f"签到成功：{sign_score}粮票"
                    logging.info(msg)
                    daily_msg += msg
                else:
                    errmsg = sign_res.text
                    logging.warning(errmsg)
                    daily_msg += errmsg
            except:
                errmsg = "签到失败，网络请求出错"
                logging.warning(errmsg)
                daily_msg += errmsg
        else:
            msg = '今天已经签到过了！'
            logging.info(msg)
            daily_msg += msg

        # 活跃积分
        active_msg ="活跃积分："
        active_id_list = score_circle_list_res.json()['activeCircleList']
        for active in active_id_list:
            active_data = f"token={self.token}&param=%7B%22token%22%3A%22{self.token}%22%2C%22scoreCircleId%22%3A{active['id']}%7D&method=gainActiveScoreCircle"
            try:
                score_daily_task_res = requests.post(self.score_url, data=active_data, headers=headers)
                # {'modifyTime': 1605683321401, 'code_': 0, 'result_': True, 'message_': '操作成功'}
                # {'code_': 22, 'result_': False, 'message_': '未到领取时间'}
                if score_daily_task_res.json()['result_']:
                    msg = f"{active['title']}获取成功：{active['foodCoupon']}粮票"
                    logging.info(msg)
                    active_msg += msg
                elif score_daily_task_res.json()['code_'] == 22:
                    msg = f"{active['title']}今天已经签到过了！"
                    logging.info(msg)
                    active_msg += msg
                else:
                    errmsg = score_daily_task_res.text
                    logging.warning(errmsg)
                    active_msg += errmsg
            except:
                errmsg = f"{active['title']}获取失败，网络请求出错"
                logging.warning(errmsg)
                active_msg += errmsg

        # 查询当前积分
        score_msg = "查询积分："
        my_score_data = f"token={self.token}&method=myScoreNewcomerTask&param=%7B%22token%22%3A%22{self.token}%22%2C%22finished%22%3A%22%22%7D"
        try:
            my_score_res = requests.post(self.score_url, data=my_score_data, headers=headers)
            if my_score_res.json()['result_']:
                msg = f"当前粮票数为：{my_score_res.json()['data']['score']}"
                logging.info(msg)
                score_msg += msg
            else:
                errmsg = "粮票数查询失败！"
                logging.warning(errmsg)
                score_msg += errmsg
        except:
            errmsg = "粮票数查询失败，网络请求出错"
            logging.info(errmsg)
            score_msg += errmsg

        return '\n'.join([daily_msg, active_msg, score_msg])

    def check_in(self):
        # 获取post提交的字段
        post_dict = self.get_post_json()
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
                                   "gpsType": 1, "token": self.token},
                      }
        response = requests.post(self.check_url, json=check_json)

        # 以json格式打印json字符串
        res = json.dumps(response.json(), sort_keys=True, indent=4, ensure_ascii=False)
        if response.json()['code'] != '10000':
            logging.warning(res)
        else:
            logging.info(res)
        # 获取积分
        score_msg = self.get_score()
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
#### 积分获取：
```
{score_msg}
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
        # logging.info(res.text)
        try:
            if not res.json()['errno']:
                logging.info('Server酱推送服务成功')
            else:
                logging.warning('Server酱推送服务失败')
        except:
            logging.warning("Server酱不起作用了，可能是你的sckey出现了问题")


if __name__ == '__main__':
    HealthyCheckIn().check_in()