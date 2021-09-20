"""
第二类健康打卡相关函数
@create：2021/03/10
@filename：healthy2_check.py
@author：ReaJason
@email_addr：reajason@163.com
@blog_website：https://reajason.top
@last_modify：2021/04/24
"""
import requests

from setting import log
from core.enum_api_url import WanXiaoServiceUrlEnum


class HealthyTwoCheck:
    def __init__(self, user_info, check_config_dict):
        self.user_info = user_info
        self.check_config_dict = check_config_dict
        self.token = user_info["token"]
        self.headers = {
            "user-agent": "Mozilla/5.0 (Linux; Android 11; Redmi K20 Pro Build/RQ3A.210805.001.A1; wv) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/93.0.4577.62 Mobile "
            "Safari/537.36 Wanxiao/5.4.2"
        }
        self.errmsg = ""

    def get_last_check_json(self):
        try:
            res = requests.post(
                url=WanXiaoServiceUrlEnum.GET_HEALTHY2_CHECK_DICT_URL.value,
                data={"token": self.token},
                headers=self.headers,
                timeout=10,
            ).json()
        except Exception as e:
            self.errmsg = f"【第二类健康获取打卡参数失败】—— 错误原因：{e}"
            return None
        if res["code"] == 0:
            return self.mix_last_check_json_and_config_dict(res["data"])
        else:
            self.errmsg = f"【第二类健康获取打卡参数失败】—— 错误原因：{res['data']}"
        return None

    def mix_last_check_json_and_config_dict(self, last_check_json):
        if not self.check_config_dict.get(
            "latitude"
        ) and not self.check_config_dict.get("longitude"):
            last_check_json["latitude"] = ""
            last_check_json["longitude"] = ""
            log.warning("第二类健康打卡未设置经纬度，后台会将此次打卡计为手动打卡（学校没做要求可不管）")
        for i, j in self.check_config_dict.items():
            if j:
                last_check_json[i] = j
        return last_check_json

    def check_in(self):
        post_dict = self.get_last_check_json()
        if not post_dict.get("whereabouts"):
            self.errmsg = f"【第二类健康打卡方式错误】—— 请选第一类健康打卡"
            return {"status": 0, "errmsg": self.errmsg}
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
            "token": self.token,
        }
        headers = {
            "referer": f"https://reportedh5.17wanxiao.com/nCovReport/index.html?token={self.token}"
            f"&customerId={self.user_info['customerId']}",
            "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
        }
        try:
            res = requests.post(
                WanXiaoServiceUrlEnum.HEALTHY2_CHECK_IN_URL.value,
                headers=headers,
                data=check_json,
                timeout=10,
            ).json()
            if res["code"] == 0:
                log.info(f"【第二类健康打卡成功】—— {res}")
                return {
                    "status": 1,
                    "res": res,
                    "post_dict": {
                        "name": post_dict["name"],
                        "updatainfo_detail": post_dict,
                        "checkbox": [
                            {"description": key, "value": value}
                            for key, value in check_json.items()
                        ],
                    },
                    "check_json": check_json,
                    "type": "healthy2",
                }
            else:
                self.errmsg = f"【第二类健康打卡失败】—— 错误原因：{res['msg']}"
                log.error(self.errmsg)
                return {"status": 0, "errmsg": self.errmsg}
        except Exception as e:
            self.errmsg = f"【第二类健康打卡失败】—— 错误原因：{e}"
            log.error(self.errmsg)
            return {"status": 0, "errmsg": self.errmsg}
