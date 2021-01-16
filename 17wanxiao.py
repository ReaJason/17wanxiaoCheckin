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
    """
    获取用户令牌，模拟登录获取：https://github.com/zhongbr/wanmei_campus
    :param username: 账号
    :param password: 密码
    :return:
    """
    user_dict = CampusCard(username, password).user_info
    if not user_dict['login']:
        return None
    return user_dict["sessionId"]


def get_post_json(jsons):
    """
    获取打卡数据
    :param jsons: 用来获取打卡数据的json字段
    :return:
    """
    retry = 0
    while retry < 3:
        try:
            res = requests.post(url="https://reportedh5.17wanxiao.com/sass/api/epmpics", json=jsons, timeout=10).json()
            # print(res)
        except:
            retry += 1
            logging.warning('获取完美校园打卡post参数失败，正在重试...')
            time.sleep(1)
            continue

        if res['code'] != '10000':
            # logging.warning(res)
            return None
        data = json.loads(res['data'])
        # print(data)
        post_dict = {
            "areaStr": 你抓取的 areaStr,
            "deptStr": 你抓取的deptStr,
            "deptid": 你抓取的deptid,
            "customerid": data['customerid'],
            "userid": data['userid'],
            "username": data['username'],
            "stuNo": 你抓取的stuNo,
            "phonenum": data['phonenum'],
            "templateid": data['templateid'],
            "updatainfo": 你抓取的updatainfo,
            "checkbox": [{"description": i["decription"], "value": i["value"]} for i in
                         data['cusTemplateRelations']],
        }
        # print(json.dumps(post_dict, sort_keys=True, indent=4, ensure_ascii=False))
        logging.info('获取完美校园打卡post参数成功')
        return post_dict
    return None


def receive_check_in(token, custom_id, post_dict):
    """
    第二类健康打卡
    :param token: 用户令牌
    :param custom_id: 健康打卡id
    :param post_dict: 健康打卡数据
    :return:
    """
    check_json = {
        "userId": post_dict['userId'],
        "name": post_dict['name'],
        "stuNo": post_dict['stuNo'],
        "whereabouts": post_dict['whereabouts'],
        "familyWhereabouts": "",
        "beenToWuhan": post_dict['beenToWuhan'],
        "contactWithPatients": post_dict['contactWithPatients'],
        "symptom": post_dict['symptom'],
        "fever": post_dict['fever'],
        "cough": post_dict['cough'],
        "soreThroat": post_dict['soreThroat'],
        "debilitation": post_dict['debilitation'],
        "diarrhea": post_dict['diarrhea'],
        "cold": post_dict['cold'],
        "staySchool": post_dict['staySchool'],
        "contacts": post_dict['contacts'],
        "emergencyPhone": post_dict['emergencyPhone'],
        "address": post_dict['address'],
        "familyForAddress": "",
        "collegeId": post_dict['collegeId'],
        "majorId": post_dict['majorId'],
        "classId": post_dict['classId'],
        "classDescribe": post_dict['classDescribe'],
        "temperature": post_dict['temperature'],
        "confirmed": post_dict['confirmed'],
        "isolated": post_dict['isolated'],
        "passingWuhan": post_dict['passingWuhan'],
        "passingHubei": post_dict['passingHubei'],
        "patientSide": post_dict['patientSide'],
        "patientContact": post_dict['patientContact'],
        "mentalHealth": post_dict['mentalHealth'],
        "wayToSchool": post_dict['wayToSchool'],
        "backToSchool": post_dict['backToSchool'],
        "haveBroadband": post_dict['haveBroadband'],
        "emergencyContactName": post_dict['emergencyContactName'],
        "helpInfo": "",
        "passingCity": "",
        "longitude": "",  # 请在此处填写需要打卡位置的longitude
        "latitude": "",  # 请在此处填写需要打卡位置的latitude
        "token": token,
    }
    headers = {
        'referer': f'https://reportedh5.17wanxiao.com/nCovReport/index.html?token={token}&customerId={custom_id}',
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8'
    }
    try:
        res = requests.post("https://reportedh5.17wanxiao.com/api/reported/receive", headers=headers, data=check_json).json()
        # 以json格式打印json字符串
        # print(res)
        if res['code'] == 0:
            logging.info(res)
            return dict(status=1, res=res, post_dict=post_dict, check_json=check_json, type='healthy')
        else:
            logging.warning(res)
            return dict(status=1, res=res, post_dict=post_dict, check_json=check_json, type='healthy')
    except:
        errmsg = f"```打卡请求出错```"
        logging.warning('打卡请求出错，网络不稳定')
        return dict(status=0, errmsg=errmsg)


def get_recall_data(token):
    """
    获取第二类健康打卡的打卡数据
    :param token: 用户令牌
    :return: 返回dict数据
    """
    retry = 0
    while retry < 3:
        try:
            res = requests.post(url="https://reportedh5.17wanxiao.com/api/reported/recall", data={"token": token}, timeout=10).json()
        except:
            retry += 1
            logging.warning('获取完美校园打卡post参数失败，正在重试...')
            time.sleep(1)
            continue
        if res['code'] == 0:
            logging.info('获取完美校园打卡post参数成功')
            return res['data']
        return None
    return None


def healthy_check_in(token, post_dict):
    """
    第一类健康打卡
    :param token: 用户令牌
    :param post_dict: 打卡数据
    :return:
    """
    check_json = {"businessType": "epmpics", "method": "submitUpInfo",
                  "jsonData": {"deptStr": post_dict['deptStr'], "areaStr": post_dict['areaStr'],
                               "reportdate": round(time.time() * 1000), "customerid": post_dict['customerid'],
                               "deptid": post_dict['deptid'], "source": "app",
                               "templateid": post_dict['templateid'], "stuNo": post_dict['stuNo'],
                               "username": post_dict['username'], "phonenum": post_dict['phonenum'],
                               "userid": post_dict['userid'], "updatainfo": post_dict['updatainfo'],
                               "gpsType": 1, "token": token},
                  }
    try:
        res = requests.post("https://reportedh5.17wanxiao.com/sass/api/epmpics", json=check_json).json()
        # 以json格式打印json字符串
        if res['code'] != '10000':
            logging.warning(res)
            return dict(status=1, res=res, post_dict=post_dict, check_json=check_json, type='healthy')
        else:
            logging.info(res)
            return dict(status=1, res=res, post_dict=post_dict, check_json=check_json, type='healthy')
    except:
        errmsg = f"```打卡请求出错```"
        logging.warning('校内打卡请求出错')
        return dict(status=0, errmsg=errmsg)


def campus_check_in(username, token, post_dict, id):
    """
    校内打卡
    :param username: 电话号
    :param token: 用户令牌
    :param post_dict: 校内打卡数据
    :param id: 校内打卡id
    :return:
    """
    check_json = {"businessType": "epmpics", "method": "submitUpInfoSchool",
                  "jsonData": {"deptStr": post_dict['deptStr'],
                               "areaStr": post_dict['areaStr'],
                               "reportdate": round(time.time() * 1000), "customerid": post_dict['customerid'],
                               "deptid": post_dict['deptid'], "source": "app",
                               "templateid": post_dict['templateid'], "stuNo": post_dict['stuNo'],
                               "username": post_dict['username'], "phonenum": username,
                               "userid": post_dict['userid'], "updatainfo": post_dict['updatainfo'],
                               "customerAppTypeRuleId": id, "clockState": 0, "token": token},
                  "token": token
                  }
    # print(check_json)
    try:
        res = requests.post("https://reportedh5.17wanxiao.com/sass/api/epmpics", json=check_json).json()

        # 以json格式打印json字符串
        if res['code'] != '10000':
            logging.warning(res)
            return dict(status=1, res=res, post_dict=post_dict, check_json=check_json, type=post_dict['templateid'])
        else:
            logging.info(res)
            return dict(status=1, res=res, post_dict=post_dict, check_json=check_json, type=post_dict['templateid'])
    except BaseException:
        errmsg = f"```校内打卡请求出错```"
        logging.warning('校内打卡请求出错')
        return dict(status=0, errmsg=errmsg)


def check_in(username, password):
    # 登录获取token用于打卡
    token = get_token(username, password)
    # print(token)
    check_dict_list = []
    # 获取现在是上午，还是下午，还是晚上
    ape_list = get_ap()

    # 获取学校使用打卡模板Id
    custom_id_dict = get_custom_id(token)

    if not token:
        errmsg = f"{username[:4]}，获取token失败，打卡失败"
        logging.warning(errmsg)
        return False

    # 获取第一类健康打卡的参数
    json1 = {"businessType": "epmpics",
             "jsonData": {"templateid": "pneumonia", "token": token},
             "method": "userComeApp"}
    post_dict = get_post_json(json1)

    if post_dict:
        # 第一类健康打卡
        # print(post_dict)

        # 修改温度等参数
        # for j in post_dict['updatainfo']:  # 这里获取打卡json字段的打卡信息，微信推送的json字段
        #     if j['propertyname'] == 'temperature':  # 找到propertyname为temperature的字段
        #         j['value'] = '36.2'  # 由于原先为null，这里直接设置36.2（根据自己学校打卡选项来）
        #     if j['propertyname'] == '举一反三即可':
        #         j['value'] = '举一反三即可'

        # 修改地址，依照自己完美校园，查一下地址即可
        # post_dict['areaStr'] = '{"streetNumber":"89号","street":"建设东路","district":"","city":"新乡市","province":"河南省",' \
        #                        '"town":"","pois":"河南师范大学(东区)","lng":113.91572178314209,' \
        #                        '"lat":35.327695868943984,"address":"牧野区建设东路89号河南师范大学(东区)","text":"河南省-新乡市",' \
        #                        '"code":""} '
        healthy_check_dict = healthy_check_in(token, post_dict)
        check_dict_list.append(healthy_check_dict)
    else:
        # 获取第二类健康打卡参数
        post_dict = get_recall_data(token)
        # 第二类健康打卡
        healthy_check_dict = receive_check_in(token, custom_id_dict['customerId'], post_dict)
        check_dict_list.append(healthy_check_dict)

    # 获取校内打卡ID
    id_list = get_id_list(token, custom_id_dict['customerAppTypeId'])
    # print(id_list)
    if not id_list:
        return check_dict_list

    # 校内打卡
    for index, i in enumerate(id_list):
        if ape_list[index]:
            # print(i)
            logging.info(f"-------------------------------{i['templateid']}-------------------------------")
            json2 = {"businessType": "epmpics",
                     "jsonData": {"templateid": i['templateid'], "customerAppTypeRuleId": i['id'],
                                  "stuNo": post_dict['stuNo'],
                                  "token": token}, "method": "userComeAppSchool",
                     "token": token}
            campus_dict = get_post_json(json2)
            campus_dict['areaStr'] = post_dict['areaStr']
            for j in campus_dict['updatainfo']:
                if j['propertyname'] == 'temperature':
                    j['value'] = '36.4'
                if j['propertyname'] == 'symptom':
                    j['value'] = '无症状'
            campus_check_dict = campus_check_in(username, token, campus_dict, i['id'])
            check_dict_list.append(campus_check_dict)
            logging.info("--------------------------------------------------------------")
    return check_dict_list


def server_push(sckey, desp):
    """
    Server酱推送：https://sc.ftqq.com/3.version
    :param sckey: 通过官网注册获取，获取教程：https://github.com/ReaJason/17wanxiaoCheckin-Actions/blob/master/README_LAST.md#%E4%BA%8Cserver%E9%85%B1%E6%9C%8D%E5%8A%A1%E7%9A%84%E7%94%B3%E8%AF%B7
    :param desp: 需要推送的内容
    :return:
    """
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


def get_custom_id(token):
    """
    用来获取custom_id，即类似与打卡模板id
    :param token: 用户令牌
    :return: return {
            'customerId': res.json()['userInfo'].get('customerId'),  # 健康打卡模板id
            'customerAppTypeId': res.json()['userInfo'].get('customerAppTypeId') # 校内打卡模板id
        }
    """
    data = {
        "appClassify": "DK",
        "token": token
    }
    try:
        res = requests.post("https://reportedh5.17wanxiao.com/api/clock/school/getUserInfo", data=data)
        # print(res.text)
        return {
            'customerId': res.json()['userInfo'].get('customerId'),
            'customerAppTypeId': res.json()['userInfo'].get('customerAppTypeId')
        }
    except:
        return None


def get_id_list(token, custom_id):
    """
    通过校内模板id获取校内打卡具体的每个时间段id
    :param token: 用户令牌
    :param custom_id: 校内打卡模板id
    :return: 返回校内打卡id列表
    """
    post_data = {
        "customerAppTypeId": custom_id,
        "longitude": "",
        "latitude": "",
        "token": token
    }
    try:
        res = requests.post("https://reportedh5.17wanxiao.com/api/clock/school/rules", data=post_data)
        # print(res.text)
        return res.json()['customerAppTypeDto']['ruleList']
    except:
        return None


def get_id_list_v1(token):
    """
    通过校内模板id获取校内打卡具体的每个时间段id（初版,暂留）
    :param token: 用户令牌
    :return: 返回校内打卡id列表
    """
    post_data = {
        "appClassify": "DK",
        "token": token
    }
    try:
        res = requests.post("https://reportedh5.17wanxiao.com/api/clock/school/childApps", data=post_data)
        if res.json()['appList']:
            id_list = sorted(res.json()['appList'][-1]['customerAppTypeRuleList'], key=lambda x: x['id'])
            res_dict = [{'id': j['id'], "templateid": f"clockSign{i + 1}"} for i, j in enumerate(id_list)]
            return res_dict
        return None
    except:
        return None


def get_ap():
    """
    获取当前时间，用于校内打卡
    :return: 返回布尔列表：[am, pm, ev]
    """
    now_time = datetime.datetime.now() + datetime.timedelta(hours=8)
    am = 0 <= now_time.hour < 12
    pm = 12 <= now_time.hour < 17
    ev = 17 <= now_time.hour <= 23
    return [am, pm, ev]


def run():
    initLogging()
    now_time = datetime.datetime.now()
    bj_time = now_time + datetime.timedelta(hours=8)
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
        check_dict = check_in(username, password)
        if not check_dict:
            return
        else:
            for check in check_dict:
                if check['post_dict'].get('checkbox'):
                    post_msg = "\n".join(
                        [f"| {i['description']} | {i['value']} |" for i in check['post_dict'].get('checkbox')])
                else:
                    post_msg = "暂无详情"
                name = check['post_dict'].get('username')
                if not name:
                    name = check['post_dict']['name']
                log_info.append(f"""#### {name}{check['type']}打卡信息：
```
{json.dumps(check['check_json'], sort_keys=True, indent=4, ensure_ascii=False)}
```

------
| Text                           | Message |
| :----------------------------------- | :--- |
{post_msg}
------
```
{check['res']}
```""")
    log_info.append(f"""
>
> [GitHub项目地址](https://github.com/ReaJason/17wanxiaoCheckin-Actions)
>
>期待你给项目的star✨
""")
    server_push(sckey, "\n".join(log_info))


if __name__ == '__main__':
    run()
