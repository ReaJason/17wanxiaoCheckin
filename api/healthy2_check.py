"""
第二类健康打卡相关函数
@create：2021/03/10
@filename：healthy2_check.py
@author：ReaJason
@email_addr：reajason@163.com
@blog_website：https://reajason.top
@last_modify：2021/04/24
"""
import time
import requests

from setting import log


def get_healthy2_check_posh_json(token):
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
            log.warning("完美校园第二类健康打卡post参数获取失败，正在重试...")
            time.sleep(1)
            continue
        if res["code"] == 0:
            log.info("完美校园第二类健康打卡post参数获取成功")
            return res["data"]
        else:
            log.warning(f"完美校园第二类健康打卡post参数获取失败，{res}")
    return None


def healthy2_check_in(token, custom_id, post_dict):
    """
    第二类健康打卡
    :param token: 用户令牌
    :param custom_id: 健康打卡id
    :param post_dict: 健康打卡数据
    :return:
    """
    if not post_dict.get("whereabouts"):
        errmsg = f"完美校园第二类健康打卡方式错误，请选第一类健康打卡"
        log.warning(errmsg)
        return {'status': 0, 'errmsg': errmsg}
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
        "classDescribe": post_dict["classDescribeAll"],
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
        "longitude": post_dict["longitude"],
        "latitude": post_dict["latitude"],
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
        log.info(res)
        return {
            'status': 1,
            'res': res,
            'post_dict': {
                'name': post_dict["name"],
                "updatainfo_detail": post_dict,
                'checkbox': [{'description': key, 'value': value} for key, value in check_json.items()]
            },
            'check_json': check_json,
            'type': "healthy2",
        }
    except:
        errmsg = f"完美校园第二类健康打卡打卡请求出错"
        log.warning(errmsg)
        return {'status': 0, 'errmsg': errmsg}
