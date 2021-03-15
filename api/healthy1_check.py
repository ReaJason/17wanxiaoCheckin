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
from setting import log


def get_healthy1_check_post_json(token):
    """
    获取打卡数据
    :param token:
    :return:
    """
    healthy1_check_post_json = {
        "businessType": "epmpics",
        "jsonData": {"templateid": "pneumonia", "token": token},
        "method": "userComeApp",
    }
    for _ in range(3):
        try:
            res = requests.post(
                url="https://reportedh5.17wanxiao.com/sass/api/epmpics",
                json=healthy1_check_post_json,
                timeout=10,
            ).json()
        except:
            log.warning("完美校园第一类健康打卡post参数获取失败，正在重试...")
            time.sleep(1)
            continue
        if res["code"] != "10000":
            """
            {'msg': '业务异常', 'code': '10007', 'data': '无法找到该机构的投票模板数据!'}
            """
            log.warning(f'完美校园第一类健康打卡post参数获取失败{res}')
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
        log.info("完美校园第一类健康打卡post参数获取成功")
        return post_dict
    return None


def healthy1_check_in(token, phone, post_dict):
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
            "phonenum": phone,
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
                log.info(res)
                return {
                    "status": 1,
                    "res": res,
                    "post_dict": post_dict,
                    "check_json": check_json,
                    "type": "healthy1",
                }
            elif res['data'] == "areaStr can not be null":
                log.warning('当前用户无法获取第一类健康打卡地址信息，请前往配置 user.json 文件，one_check 下的 areaStr 设置地址信息')
            elif "频繁" in res['data']:
                log.info(res)
                return {
                    "status": 1,
                    "res": res,
                    "post_dict": post_dict,
                    "check_json": check_json,
                    "type": "healthy1",
                }
            else:
                log.warning(res)
                return {"status": 0, "errmsg": f"{post_dict['username']}: {res}"}
        except:
            errmsg = f"```打卡请求出错```"
            log.warning("健康打卡请求出错")
            return {"status": 0, "errmsg": errmsg}
    return {"status": 0, "errmsg": "健康打卡请求出错"}
