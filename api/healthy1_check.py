"""
第一类健康打卡相关函数
@create：2021/03/10
@filename：healthy1_check.py
@author：ReaJason
@email_addr：reajason@163.com
@blog_website：https://reajason.top
@last_modify：2021/03/15
"""
import logging
import time
import json
import requests

from utils.Errors import *


def get_healthy1_check_post_json(user, templateid):
    """
    获取打卡数据
    :param token:
    :return:
    """
    log = logging.getLogger('main.'+user['username'])
    healthy1_check_post_json = {
        "businessType": "epmpics",
        "jsonData": {"templateid": templateid, "token": user['token']},
        "method": "userComeApp",
    }
    res = requests.post(
        url="https://reportedh5.17wanxiao.com/sass/api/epmpics",
        json=healthy1_check_post_json,
        timeout=30,
        )
    res.raise_for_status()
    res=res.json()
    if '会话失效'in res['data']:
        raise NotLoginError
    elif res["code"] != "10000":
        """
        {'msg': '业务异常', 'code': '10007', 'data': '无法找到该机构的投票模板数据!'}
        """
        log.warning(f'完美校园第一类健康打卡post参数获取失败{res}')
        raise Exception(res)
    data = json.loads(res["data"])
    post_dict = {
        "areaStr": data['areaStr'],
        "ver": data["ver"],
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
            {"description": i["decription"], "value": i["value"],
                "propertyname": i["propertyname"]}
            for i in data["cusTemplateRelations"]
        ],
    }
    log.info("完美校园第一类健康打卡post参数获取成功")
    return post_dict


def healthy1_check_in(user, post_dict):
    """
    第一类健康打卡
    :param phone: 手机号
    :param token: 用户令牌
    :param post_dict: 打卡数据
    :return:
    """
    log = logging.getLogger('main.'+user['username'])
    check_json = {
        "businessType": "epmpics",
        "method": "submitUpInfo",
        "jsonData": {
            "deptStr": post_dict["deptStr"],
            "areaStr": post_dict["areaStr"],
            "reportdate": round(time.time() * 1000),
            "customerid": post_dict["customerid"],
            "deptid": post_dict['deptStr']['deptid'] if post_dict['deptStr'] else None,
            "source": "app",
            "templateid": post_dict["templateid"],
            "stuNo": post_dict["stuNo"],
            "username": post_dict["username"],
            "phonenum": user['username'],
            "userid": post_dict["userid"],
            "updatainfo": post_dict["updatainfo"],
            "gpsType": 1,
            "ver": post_dict["ver"],
            "token": user['token'],
        },
    }
    res = requests.post(
        "https://reportedh5.17wanxiao.com/sass/api/epmpics", json=check_json
    )
    res.raise_for_status()
    res = res.json()
    if res['code'] == '10000' or "频繁" in res['data']:
        log.info('打卡成功')
    elif res['data'] == "areaStr can not be null":
        log.error(
            '当前用户无法获取第一类健康打卡地址信息，请前往配置 user.json 文件，one_check 下的 areaStr 设置地址信息')
    else:
        log.error(res)
