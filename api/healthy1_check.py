"""
第一类健康打卡相关函数
@create：2021/03/10
@filename：healthy1_check.py
@author：ReaJason
@email_addr：reajason@163.com
@blog_website：https://reajason.top
@last_modify：2021/03/15
"""
import time
import json
import requests


def get_healthy1_check_post_json(token, templateid):
    """
    获取打卡数据
    :param token:
    :return:
    """
    healthy1_check_post_json = {
        "businessType": "epmpics",
        "jsonData": {"templateid": templateid, "token": token},
        "method": "userComeApp",
    }
    try:
        res = requests.post(
            url="https://reportedh5.17wanxiao.com/sass/api/epmpics",
            json=healthy1_check_post_json,
        )
        res.raise_for_status()
        res = res.json()
    except Exception as e:
        # log.warning("完美校园第一类健康打卡post参数获取失败，正在重试...")
        # time.sleep(3)
        # continue
        raise Exception(*('打卡参数获取失败',)+e.args)
    if "会话失效" in res['data']:
        return 1
    if res["code"] != "10000":
        """
        {'msg': '业务异常', 'code': '10007', 'data': '无法找到该机构的投票模板数据!'}
        """
        raise Exception(
            '打卡参数获取失败', 'code: '+res['code'], 'msg: '+res['msg'], 'data: '+res['data'])
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
    return post_dict


def healthy1_check_in(user, post_dict):
    """
    第一类健康打卡
    :param phone: 手机号
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
    try:
        res = requests.post(
            "https://reportedh5.17wanxiao.com/sass/api/epmpics", json=check_json
        )
        res.raise_for_status()
        res = res.json()
        if res['code'] == '10000':
            #  log.info(res)
            return {
                "status": 1,
                "res": res,
                "post_dict": post_dict,
                "check_json": check_json,
                "type": "healthy1",
            }
        elif res['data'] == "areaStr can not be null":
            raise Exception('当前用户无法获取第一类健康打卡地址信息')
        elif "频繁" in res['data']:
            return {
                "status": 1,
                "res": res,
                "post_dict": post_dict,
                "check_json": check_json,
                "type": "healthy1",
            }
        elif "token" in res['data']:
            return {"status": 2, }
        else:
            raise Exception(res)
    except Exception as e:
        raise Exception(*('健康打卡请求出错',)+e.args)
