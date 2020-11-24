import time
import datetime
import json
import logging
import requests

from login import CampusCard


def initLogging():
    logging.getLogger().setLevel(logging.INFO)
    logging.basicConfig(format="[%(levelname)s]; %(message)s")


def get_token(username, password):
    user_dict = CampusCard(username, password).user_info
    if not user_dict['login']:
        return None
    return user_dict["sessionId"]


def get_post_json(token):
    retry = 0
    while retry < 3:
        jsons = {"businessType": "epmpics",
                 "jsonData": {"templateid": "pneumonia", "token": token},
                 "method": "userComeApp"}
        try:
            # 如果不请求一下这个地址，token就会失效
            requests.post("https://reportedh5.17wanxiao.com/api/clock/school/getUserInfo", data={'token': token})
            res = requests.post(url="https://reportedh5.17wanxiao.com/sass/api/epmpics", json=jsons, timeout=10).json()
        except:
            retry += 1
            logging.warning('获取完美校园打卡post参数失败，正在重试...')
            time.sleep(1)
            continue
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
    return None


def check_in(username, password):
    token = get_token(username, password)
    if not token:
        errmsg = f"{username}，获取token失败，打卡失败"
        logging.warning(errmsg)
        return dict(status=0, errmsg=errmsg)

    post_dict = get_post_json(token)
    if not post_dict:
        errmsg = f'{username}，获取完美校园打卡post参数失败'
        logging.warning(errmsg)
        return dict(status=0, errmsg=errmsg)
    check_json = {"businessType": "epmpics", "method": "submitUpInfo",
                  "jsonData": {"deptStr": post_dict['deptStr'], "areaStr": post_dict['areaStr'],
                               "reportdate": round(time.time() * 1000), "customerid": post_dict['customerid'],
                               "deptid": post_dict['deptid'], "source": "app",
                               "templateid": post_dict['templateid'], "stuNo": post_dict['stuNo'],
                               "username": post_dict['username'], "phonenum": username,
                               "userid": post_dict['userid'], "updatainfo": post_dict['updatainfo'],
                               "gpsType": 1, "token": token},
                  }
    try:
        response = requests.post("https://reportedh5.17wanxiao.com/sass/api/epmpics", json=check_json)
    except:
        errmsg = f"```{username}，打卡请求出错```"
        logging.warning(errmsg)
        return dict(status=0, errmsg=errmsg)

    # 以json格式打印json字符串
    res = json.dumps(response.json(), sort_keys=True, indent=4, ensure_ascii=False)
    if response.json()['code'] != '10000':
        logging.warning(res)
        return dict(status=1, res=res, post_dict=post_dict, check_json=check_json)
    else:
        logging.info(res)
        return dict(status=1, res=res, post_dict=post_dict, check_json=check_json)


def server_push(sckey, desp):
    send_url = f"https://sc.ftqq.com/{sckey}.send"
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


def run():
    initLogging()
    now_time = datetime.datetime.now()
    bj_time = now_time + datetime.timedelta(hours=8)
    test_day = datetime.datetime.strptime('2020-12-26 00:00:00', '%Y-%m-%d %H:%M:%S')
    date = (test_day - bj_time).days
    log_info = [f"""
------
#### 现在时间：
```
{bj_time.strftime("%Y-%m-%d %H:%M:%S %p")}
```"""]
    username_list = input().split(',')
    password_list = input().split(',')
    sckey = input()
    for username, password in zip([i.strip() for i in username_list if i != ''],
                                  [i.strip() for i in password_list if i != '']):
        chech_dict = check_in(username, password)
        if not chech_dict['status']:
            log_info.append(chech_dict['errmsg'])
        else:
            post_msg = "\n".join([f"| {i['description']} | {i['value']} |" for i in chech_dict['post_dict']['checkbox']])
            log_info.append(f"""#### {chech_dict['post_dict']['username']}打卡json字段：
```
{json.dumps(chech_dict['check_json'], sort_keys=True, indent=4, ensure_ascii=False)}
```
#### {chech_dict['post_dict']['username']}打卡信息：
------
| Text                           | Message |
| :----------------------------------- | :--- |
{post_msg}
------
```
{chech_dict['res']}
```
            """)
    log_info.append(f"""### ⚡考研倒计时:
```
{date}天
```

>
> [GitHub项目地址](https://github.com/ReaJason/17wanxiaoCheckin-Actions)
>
>期待你给项目的star✨
""")
    server_push(sckey, "\n".join(log_info))


if __name__ == '__main__':
    run()