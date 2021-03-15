"""
校内打卡相关函数
@create：2021/03/10
@filename：campus_check.py
@author：ReaJason
@email_addr：reajason@163.com
@blog_website：https://reajason.top
@last_modify：2021/03/15
"""
import time
import json

import requests

from setting import log


def get_id_list_v2(token, custom_type_id):
    """
    通过校内模板id获取校内打卡具体的每个时间段id
    :param token: 用户令牌
    :param custom_type_id: 校内打卡模板id
    :return: 返回校内打卡id列表
    """
    post_data = {
        "customerAppTypeId": custom_type_id,
        "longitude": "",
        "latitude": "",
        "token": token,
    }
    try:
        res = requests.post(
            "https://reportedh5.17wanxiao.com/api/clock/school/rules", data=post_data
        )
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
        ).json()
        if res.json()["appList"]:
            app_list = res["appList"][-1]["customerAppTypeRuleList"] \
                if res["appList"][-1]["customerAppTypeRuleList"] \
                else res["appList"][0]["customerAppTypeRuleList"]
            id_list = sorted(
                app_list,
                key=lambda x: x["id"],
            )
            res_dict = [
                {"customerAppTypeId": j["id"], "templateid": f"clockSign{i + 1}"}
                for i, j in enumerate(id_list)
            ]
            return res_dict
        return None
    except:
        return None
    
    
def get_customer_type_id(token):
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
        ).json()
        for app in res["appList"]:
            if '校内' in app['name']:
                return app['id']
    except:
        return None


def get_campus_check_post(template_id, custom_rule_id, stu_num, token):
    """
    获取打卡数据
    :param template_id:
    :param custom_rule_id:
    :param stu_num:
    :param token:
    :return:
    """
    campus_check_post_json = {
        "businessType": "epmpics",
        "jsonData": {
            "templateid": template_id,
            "customerAppTypeRuleId": custom_rule_id,
            "stuNo": stu_num,
            "token": token
        },
        "method": "userComeAppSchool",
        "token": token
    }
    for _ in range(3):
        try:
            res = requests.post(
                url="https://reportedh5.17wanxiao.com/sass/api/epmpics",
                json=campus_check_post_json,
                timeout=10,
            ).json()
        except:
            log.warning("完美校园校内打卡post参数获取失败，正在重试...")
            time.sleep(1)
            continue
        if res["code"] != "10000":
            """
            {'msg': '业务异常', 'code': '10007', 'data': '无法找到该机构的投票模板数据!'}
            """
            log.warning(res['data'])
            return None
        data = json.loads(res["data"])
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
        log.info("完美校园校内打卡post参数获取成功")
        return post_dict
    return None


def campus_check_in(phone, token, post_dict, custom_rule_id):
    """
    校内打卡
    :param phone: 电话号
    :param token: 用户令牌
    :param post_dict: 校内打卡数据
    :param custom_rule_id: 校内打卡id
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
            "phonenum": phone,
            "userid": post_dict["userid"],
            "updatainfo": post_dict["updatainfo"],
            "customerAppTypeRuleId": custom_rule_id,
            "clockState": 0,
            "token": token,
        },
        "token": token,
    }
    try:
        res = requests.post(
            "https://reportedh5.17wanxiao.com/sass/api/epmpics", json=check_json
        ).json()
        """
        {'msg': '业务异常', 'code': '10007', 'data': '请在正确的打卡时间打卡'}
        """
        if res["code"] == "10000":
            log.info(res)
        elif res['data'] == "areaStr can not be null":
            log.warning("当前用户无法获取校内打卡地址信息，请前往配置文件，campus_checkin 下的 areaStr 设置地址信息")
        elif res['data'] == "请在正确的打卡时间打卡":
            log.warning( f'当前已不在该打卡时间范围内，{res["data"]}')
        else:
            log.warning(res)
        return {
            'status': 1,
            'res': res,
            'post_dict': post_dict,
            'check_json': check_json,
            'type': post_dict["templateid"]
        }
    except:
        errmsg = f"```校内打卡请求出错```"
        log.warning("校内打卡请求出错")
        return {'status': 0, 'errmsg': errmsg}
