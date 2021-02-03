import time
import os
import datetime
import json
import logging
import requests

from utils.server_chan import server_push
from utils.qq_email import qq_email_push
from utils.qmsg import qmsg_push
from login import CampusLogin


def initLogging():
    logging.getLogger().setLevel(logging.INFO)
    logging.basicConfig(format="[%(levelname)s]; %(message)s")


def get_token(username, password, device_id):
    """
    获取用户令牌，模拟登录获取：https://github.com/zhongbr/wanmei_campus
    :param device_id: 设备ID
    :param username: 账号
    :param password: 密码
    :return:
    """
    for _ in range(3):
        try:
            campus_login = CampusLogin(phone_num=username, device_id=device_id)
        except Exception as e:
            logging.warning(e)
            continue
        login_dict = campus_login.pwd_login(password)
        if login_dict["status"]:
            logging.info(f"{username[:4]}，{login_dict['msg']}")
            return login_dict["token"]
        elif login_dict['errmsg'] == "该手机号未注册完美校园":
            logging.warning(f"{username[:4]}，{login_dict['errmsg']}")
            return None
        elif login_dict['errmsg'].startswith("密码错误"):
            logging.warning(f"{username[:4]}，{login_dict['errmsg']}")
            logging.warning("代码是死的，密码错误了就是错误了，赶紧去查看一下是不是输错了!")
            return None
        else:
            logging.info(f"{username[:4]}，{login_dict['errmsg']}")
            logging.warning('正在尝试重新登录......')
            time.sleep(5)
    return None


def get_school_name(token):
    post_data = {"token": token, "method": "WX_BASE_INFO", "param": "%7B%7D"}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    try:
        res = requests.post(
            "https://server.59wanmei.com/YKT_Interface/xyk",
            data=post_data,
            headers=headers,
        )
        return res.json()["data"]["customerName"]
    except:
        return "泪目，没获取到学校名字"


def get_user_info(token):
    """
    用来获取custom_id，即类似与打卡模板id
    :param token: 用户令牌
    :return: return
    """
    data = {"appClassify": "DK", "token": token}
    for _ in range(3):
        try:
            res = requests.post(
                "https://reportedh5.17wanxiao.com/api/clock/school/getUserInfo", data=data
            )
            user_info = res.json()["userInfo"]
            logging.info('获取个人信息成功')
            return user_info
        except:
            logging.warning('获取个人信息失败，正在重试......')
            time.sleep(1)
    return None


def get_post_json(post_json):
    """
    获取打卡数据
    :param jsons: 用来获取打卡数据的json字段
    :return:
    """
    for _ in range(3):
        try:
            res = requests.post(
                url="https://reportedh5.17wanxiao.com/sass/api/epmpics",
                json=post_json,
                timeout=10,
            ).json()
        except:
            logging.warning("获取完美校园打卡post参数失败，正在重试...")
            time.sleep(1)
            continue
        if res["code"] != "10000":
            logging.warning(res)
        data = json.loads(res["data"])
        # print(data)
        post_dict = {
            "areaStr": data['areaStr'],
            "deptStr": data['deptStr'],
            "deptid": data['deptStr']['deptid'] if data['deptStr'] else None,
            "customerid": data['customerid'],
            "userid": data['userid'],
            "username": data['username'],
            "stuNo": data['stuNo'],
            "phonenum": data["phonenum"],
            "templateid": data["templateid"],
            "updatainfo": [
                {"propertyname": i["propertyname"], "value": i["value"]}
                for i in data["cusTemplateRelations"]
            ],
            "updatainfo_detail": [
                {
                    "propertyname": i["propertyname"],
                    "checkValues": i["checkValues"],
                    "description": i["decription"],
                    "value": i["value"],
                }
                for i in data["cusTemplateRelations"]
            ],
            "checkbox": [
                {"description": i["decription"], "value": i["value"], "propertyname": i["propertyname"]}
                for i in data["cusTemplateRelations"]
            ],
        }
        # print(json.dumps(post_dict, sort_keys=True, indent=4, ensure_ascii=False))
        logging.info("获取完美校园打卡post参数成功")
        return post_dict
    return None


def healthy_check_in(token, username, post_dict):
    """
    第一类健康打卡
    :param username: 手机号
    :param token: 用户令牌
    :param post_dict: 打卡数据
    :return:
    """
    check_json = {
        "businessType": "epmpics",
        "method": "submitUpInfo",
        "jsonData": {
            "deptStr": post_dict["deptStr"],
            "areaStr": post_dict["areaStr"],
            "reportdate": round(time.time() * 1000),
            "customerid": post_dict["customerid"],
            "deptid": post_dict["deptid"],
            "source": "app",
            "templateid": post_dict["templateid"],
            "stuNo": post_dict["stuNo"],
            "username": post_dict["username"],
            "phonenum": username,
            "userid": post_dict["userid"],
            "updatainfo": post_dict["updatainfo"],
            "gpsType": 1,
            "token": token,
        },
    }
    for _ in range(3):
        try:
            res = requests.post(
                "https://reportedh5.17wanxiao.com/sass/api/epmpics", json=check_json
            ).json()
            if res['code'] == '10000':
                logging.info(res)
                return {
                    "status": 1,
                    "res": res,
                    "post_dict": post_dict,
                    "check_json": check_json,
                    "type": "healthy",
                }
            elif "频繁" in res['data']:
                logging.info(res)
                return {
                    "status": 1,
                    "res": res,
                    "post_dict": post_dict,
                    "check_json": check_json,
                    "type": "healthy",
                }
            else:
                logging.warning(res)
                return {"status": 0, "errmsg": f"{post_dict['username']}: {res}"}
        except:
            errmsg = f"```打卡请求出错```"
            logging.warning("健康打卡请求出错")
            return {"status": 0, "errmsg": errmsg}
    return {"status": 0, "errmsg": "健康打卡请求出错"}


def get_recall_data(token):
    """
    获取第二类健康打卡的打卡数据
    :param token: 用户令牌
    :return: 返回dict数据
    """
    for _ in range(3):
        try:
            res = requests.post(
                url="https://reportedh5.17wanxiao.com/api/reported/recall",
                data={"token": token},
                timeout=10,
            ).json()
        except:
            logging.warning("获取完美校园打卡post参数失败，正在重试...")
            time.sleep(1)
            continue
        if res["code"] == 0:
            logging.info("获取完美校园打卡post参数成功")
            return res["data"]
        else:
            logging.warning(res)
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
        "userId": post_dict["userId"],
        "name": post_dict["name"],
        "stuNo": post_dict["stuNo"],
        "whereabouts": post_dict["whereabouts"],
        "familyWhereabouts": "",
        "beenToWuhan": post_dict["beenToWuhan"],
        "contactWithPatients": post_dict["contactWithPatients"],
        "symptom": post_dict["symptom"],
        "fever": post_dict["fever"],
        "cough": post_dict["cough"],
        "soreThroat": post_dict["soreThroat"],
        "debilitation": post_dict["debilitation"],
        "diarrhea": post_dict["diarrhea"],
        "cold": post_dict["cold"],
        "staySchool": post_dict["staySchool"],
        "contacts": post_dict["contacts"],
        "emergencyPhone": post_dict["emergencyPhone"],
        "address": post_dict["address"],
        "familyForAddress": "",
        "collegeId": post_dict["collegeId"],
        "majorId": post_dict["majorId"],
        "classId": post_dict["classId"],
        "classDescribe": post_dict["classDescribe"],
        "temperature": post_dict["temperature"],
        "confirmed": post_dict["confirmed"],
        "isolated": post_dict["isolated"],
        "passingWuhan": post_dict["passingWuhan"],
        "passingHubei": post_dict["passingHubei"],
        "patientSide": post_dict["patientSide"],
        "patientContact": post_dict["patientContact"],
        "mentalHealth": post_dict["mentalHealth"],
        "wayToSchool": post_dict["wayToSchool"],
        "backToSchool": post_dict["backToSchool"],
        "haveBroadband": post_dict["haveBroadband"],
        "emergencyContactName": post_dict["emergencyContactName"],
        "helpInfo": "",
        "passingCity": "",
        "longitude": "",  # 请在此处填写需要打卡位置的longitude
        "latitude": "",  # 请在此处填写需要打卡位置的latitude
        "token": token,
    }
    headers = {
        "referer": f"https://reportedh5.17wanxiao.com/nCovReport/index.html?token={token}&customerId={custom_id}",
        "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
    }
    try:
        res = requests.post(
            "https://reportedh5.17wanxiao.com/api/reported/receive",
            headers=headers,
            data=check_json,
        ).json()
        # 以json格式打印json字符串
        # print(res)
        if res["code"] == 0:
            logging.info(res)
            return dict(
                status=1,
                res=res,
                post_dict=post_dict,
                check_json=check_json,
                type="healthy",
            )
        else:
            logging.warning(res)
            return dict(
                status=1,
                res=res,
                post_dict=post_dict,
                check_json=check_json,
                type="healthy",
            )
    except:
        errmsg = f"```打卡请求出错```"
        logging.warning("打卡请求出错，网络不稳定")
        return dict(status=0, errmsg=errmsg)


def get_ap():
    """
    获取当前时间，用于校内打卡
    :return: 返回布尔列表：[am, pm, ev]
    """
    now_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    am = 0 <= now_time.hour < 12
    pm = 12 <= now_time.hour < 17
    ev = 17 <= now_time.hour <= 23
    return [am, pm, ev]


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
        "token": token,
    }
    try:
        res = requests.post(
            "https://reportedh5.17wanxiao.com/api/clock/school/rules", data=post_data
        )
        # print(res.text)
        return res.json()["customerAppTypeDto"]["ruleList"]
    except:
        return None


def get_id_list_v1(token):
    """
    通过校内模板id获取校内打卡具体的每个时间段id（初版,暂留）
    :param token: 用户令牌
    :return: 返回校内打卡id列表
    """
    post_data = {"appClassify": "DK", "token": token}
    try:
        res = requests.post(
            "https://reportedh5.17wanxiao.com/api/clock/school/childApps",
            data=post_data,
        )
        if res.json()["appList"]:
            id_list = sorted(
                res.json()["appList"][-1]["customerAppTypeRuleList"],
                key=lambda x: x["id"],
            )
            res_dict = [
                {"id": j["id"], "templateid": f"clockSign{i + 1}"}
                for i, j in enumerate(id_list)
            ]
            return res_dict
        return None
    except:
        return None


def campus_check_in(username, token, post_dict, id):
    """
    校内打卡
    :param username: 电话号
    :param token: 用户令牌
    :param post_dict: 校内打卡数据
    :param id: 校内打卡id
    :return:
    """
    check_json = {
        "businessType": "epmpics",
        "method": "submitUpInfoSchool",
        "jsonData": {
            "deptStr": post_dict["deptStr"],
            "areaStr": post_dict["areaStr"],
            "reportdate": round(time.time() * 1000),
            "customerid": post_dict["customerid"],
            "deptid": post_dict["deptid"],
            "source": "app",
            "templateid": post_dict["templateid"],
            "stuNo": post_dict["stuNo"],
            "username": post_dict["username"],
            "phonenum": username,
            "userid": post_dict["userid"],
            "updatainfo": post_dict["updatainfo"],
            "customerAppTypeRuleId": id,
            "clockState": 0,
            "token": token,
        },
        "token": token,
    }
    # print(check_json)
    try:
        res = requests.post(
            "https://reportedh5.17wanxiao.com/sass/api/epmpics", json=check_json
        ).json()
        
        # 以json格式打印json字符串
        if res["code"] != "10000":
            logging.warning(res)
            return dict(
                status=1,
                res=res,
                post_dict=post_dict,
                check_json=check_json,
                type=post_dict["templateid"],
            )
        else:
            logging.info(res)
            return dict(
                status=1,
                res=res,
                post_dict=post_dict,
                check_json=check_json,
                type=post_dict["templateid"],
            )
    except BaseException:
        errmsg = f"```校内打卡请求出错```"
        logging.warning("校内打卡请求出错")
        return dict(status=0, errmsg=errmsg)


def check_in(username, password, device_id):
    check_dict_list = []
    
    # 登录获取token用于打卡
    token = get_token(username, password, device_id)
    
    if not token:
        errmsg = f"{username[:4]}，获取token失败，打卡失败"
        logging.warning(errmsg)
        check_dict_list.append({"status": 0, "errmsg": errmsg})
        return check_dict_list
    
    # print(token)
    # 获取现在是上午，还是下午，还是晚上
    # ape_list = get_ap()
    
    # 获取学校使用打卡模板Id
    user_info = get_user_info(token)
    if not user_info:
        errmsg = f"{username[:4]}，获取user_info失败，打卡失败"
        logging.warning(errmsg)
        check_dict_list.append({"status": 0, "errmsg": errmsg})
        return check_dict_list
    
    # 获取第一类健康打卡的参数
    json1 = {
        "businessType": "epmpics",
        "jsonData": {"templateid": "pneumonia", "token": token},
        "method": "userComeApp",
    }
    post_dict = get_post_json(json1)
    
    if post_dict:
        # 第一类健康打卡
        # print(post_dict)
        
        # 修改温度等参数
        # for j in post_dict['updatainfo']:  # 这里获取打卡json字段的打卡信息，微信推送的json字段
        #     if j['propertyname'] == 'temperature':  # 找到propertyname为temperature的字段
        #         j['value'] = '36.2'  # 由于原先为null，这里直接设置36.2（根据自己学校打卡选项来）
        #     if j['propertyname'] == 'xinqing':
        #         j['value'] = '健康'
        #     if j['propertyname'] == 'outdoor':
        #         j['value'] = '否'
        #     if j['propertyname'] == 'symptom':
        #         j['value'] = '无症状'
        #     if j['propertyname'] == 'ownbodyzk':
        #         j['value'] = '身体健康，无异常'
        
        # 修改地址，依照自己完美校园，查一下地址即可
        # post_dict['areaStr'] = '{"streetNumber":"89号","street":"建设东路","district":"","city":"新乡市","province":"河南省",' \
        #                        '"town":"","pois":"河南师范大学(东区)","lng":113.91572178314209,' \
        #                        '"lat":35.327695868943984,"address":"牧野区建设东路89号河南师范大学(东区)","text":"河南省-新乡市",' \
        #                        '"code":""} '
        healthy_check_dict = healthy_check_in(token, username, post_dict)
        check_dict_list.append(healthy_check_dict)
    else:
        # 获取第二类健康打卡参数
        post_dict = get_recall_data(token)
        # 第二类健康打卡
        healthy_check_dict = receive_check_in(token, user_info["customerId"], post_dict)
        check_dict_list.append(healthy_check_dict)
    
    # # 获取校内打卡ID
    # id_list = get_id_list(token, user_info.get('customerAppTypeId'))
    # # print(id_list)
    # if not id_list:
    #     return check_dict_list
    #
    # # 校内打卡
    # for index, i in enumerate(id_list):
    #     if ape_list[index]:
    #         # print(i)
    #         logging.info(f"-------------------------------{i['templateid']}-------------------------------")
    #         json2 = {"businessType": "epmpics",
    #                  "jsonData": {"templateid": i['templateid'], "customerAppTypeRuleId": i['id'],
    #                               "stuNo": post_dict['stuNo'],
    #                               "token": token}, "method": "userComeAppSchool",
    #                  "token": token}
    #         campus_dict = get_post_json(json2)
    #         campus_dict['areaStr'] = post_dict['areaStr']
    #         for j in campus_dict['updatainfo']:
    #             if j['propertyname'] == 'temperature':
    #                 j['value'] = '36.4'
    #             if j['propertyname'] == 'symptom':
    #                 j['value'] = '无症状'
    #         campus_check_dict = campus_check_in(username, token, campus_dict, i['id'])
    #         check_dict_list.append(campus_check_dict)
    #         logging.info("--------------------------------------------------------------")
    return check_dict_list


def wanxiao_server_push(sckey, check_info_list):
    utc8_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    push_list = [f"""
------
#### 现在时间：
```
{utc8_time.strftime("%Y-%m-%d %H:%M:%S %p")}
```"""]
    for check_info in check_info_list:
        if check_info["status"]:
            if check_info["post_dict"].get("checkbox"):
                post_msg = "\n".join(
                    [
                        f"| {i['description']} | {j['value']} |"
                        for i in check_info["post_dict"].get("checkbox")
                        for j in check_info["post_dict"].get("updatainfo")
                        if i["propertyname"] == j["propertyname"]
                    ]
                )
            else:
                post_msg = "暂无详情"
            name = check_info["post_dict"].get("username")
            if not name:
                name = check_info["post_dict"]["name"]
            push_list.append(
                f"""#### {name}{check_info['type']}打卡信息：
```
{json.dumps(check_info['check_json'], sort_keys=True, indent=4, ensure_ascii=False)}
```
------
| Text                           | Message |
| :----------------------------------- | :--- |
{post_msg}
------
```
{check_info['res']}
```"""
            )
        else:
            push_list.append(
                f"""------
#### {check_info['errmsg']}
------
"""
            )
    push_list.append(
        f"""
>
> [17wanxiaoCheckin-Actions](https://github.com/ReaJason/17wanxiaoCheckin-Actions)
>
>期待你给项目的star✨
"""
    )
    return server_push(sckey, "健康打卡", "\n".join(push_list))


def wanxiao_qq_mail_push(send_email, send_pwd, receive_email, check_info_list):
    bj_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    bj_time.strftime("%Y-%m-%d %H:%M:%S %p")
    mail_msg_list = [f"""
<h2><center> >>>>  <a href="https://github.com/ReaJason/17wanxiaoCheckin-Actions">17wanxiaoCheckin-Actions</a>
<<<<</center></h2>
<h2><center>期待你的Star✨</center></h2>
<h3><center>打卡时间：{bj_time}</center></h3>
"""
                     ]
    for check in check_info_list:
        if check["status"]:
            name = check['post_dict'].get('username')
            if not name:
                name = check['post_dict']['name']
            mail_msg_list.append(f"""<hr>
<details>
<summary style="font-family: 'Microsoft YaHei UI',serif; color: deepskyblue;">{name}：{check["type"]} 打卡结果：{check['res']}</summary>
<pre><code>
{json.dumps(check['check_json'], sort_keys=True, indent=4, ensure_ascii=False)}
</code></pre>
</details>
<details>
<summary style="font-family: 'Microsoft YaHei UI',serif; color: black;" >>>>填写数据抓包详情（便于代码的编写）<<<</summary>
<pre><code>
{json.dumps(check['post_dict']['updatainfo_detail'], sort_keys=True, indent=4, ensure_ascii=False)}
</code></pre>
</details>
<details>
<summary style="font-family: 'Microsoft YaHei UI',serif; color: lightskyblue;" >>>>打卡信息数据表格<<<</summary>
<table id="customers">
<tr>
<th>Text</th>
<th>Value</th>
</tr>
"""
                                 )
            for index, box in enumerate(check["post_dict"]["checkbox"]):
                if index % 2:
                    mail_msg_list.append(
                        f"""<tr>
<td>{box['description']}</td>
<td>{box['value']}</td>
</tr>"""
                    )
                else:
                    mail_msg_list.append(f"""<tr class="alt">
<td>{box['description']}</td>
<td>{box['value']}</td>
</tr>"""
                                         )
            mail_msg_list.append(
                f"""
</table></details>"""
            )
        else:
            mail_msg_list.append(
                f"""<hr>
    <b style="color: red">{check['errmsg']}</b>"""
            )
    css = """<style type="text/css">
#customers
  {
  font-family:"Trebuchet MS", Arial, Helvetica, sans-serif;
  width:100%;
  border-collapse:collapse;
  }

#customers td, #customers th
  {
  font-size:1em;
  border:1px solid #98bf21;
  padding:3px 7px 2px 7px;
  }

#customers th
  {
  font-size:1.1em;
  text-align:left;
  padding-top:5px;
  padding-bottom:4px;
  background-color:#A7C942;
  color:#ffffff;
  }

#customers tr.alt td
  {
  color:#000000;
  background-color:#EAF2D3;
  }
</style>"""
    mail_msg_list.append(css)
    return qq_email_push(send_email, send_pwd, receive_email,
                         title="完美校园健康打卡", text="".join(mail_msg_list))


def wanxiao_qmsg_push(key, qq_num, check_info_list, send_type):
    utc8_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    push_list = [f'@face=74@ {utc8_time.strftime("%Y-%m-%d %H:%M:%S")} @face=74@ ']
    for check_info in check_info_list:
        if check_info["status"]:
            name = check_info["post_dict"].get("username")
            if not name:
                name = check_info["post_dict"]["name"]
            push_list.append(f"""\
@face=54@ {name}{check_info['type']} @face=54@
@face=211@
{check_info['res']}
@face=211@""")
        else:
            push_list.append(check_info['errmsg'])
    return qmsg_push(key, qq_num, "\n".join(push_list), send_type)


def main_handler(*args, **kwargs):
    initLogging()
    raw_info = []
    username_list = os.environ['USERNAME'].split(',')
    password_list = os.environ['PASSWORD'].split(',')
    device_id_list = os.environ['DEVICEID'].split(',')
    sckey = os.environ.get('SCKEY')
    key = os.environ.get('KEY')
    qq_num = os.environ.get('QQ_NUM')
    send_email = os.environ.get('SEND_EMAIL')
    send_pwd = os.environ.get('SEND_PWD')
    receive_email = os.environ.get('RECEIVE_EMAIL')
    for username, password, device_id in zip(
            [i.strip() for i in username_list if i != ''],
            [i.strip() for i in password_list if i != ''],
            [i.strip() for i in device_id_list if i != '']):
        check_dict = check_in(username, password, device_id)
        raw_info.extend(check_dict)
    if sckey:
        logging.info(wanxiao_server_push(sckey, raw_info))
    if send_email and send_pwd and receive_email:
        logging.info(wanxiao_qq_mail_push(send_email, send_pwd, receive_email, raw_info))
    if key:
        logging.info(wanxiao_qmsg_push(key, qq_num, raw_info, send_type="send"))


if __name__ == "__main__":
    main_handler()
