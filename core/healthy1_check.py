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
from setting import log
from core.base_check import BaseCheck


class HealthyOneCheck(BaseCheck):
    def __init__(self, user_info, check_config_dict):
        super().__init__(user_info, check_config_dict)

    def check_in(self):
        healthy1_check_post_json = {
            "businessType": "epmpics",
            "jsonData": {"templateid": "pneumonia", "token": self.token},
            "method": "userComeApp",
        }
        post_dict = self.get_last_check_json(healthy1_check_post_json)
        if not post_dict:
            log.error(self.errmsg)
            return {"status": 0, "errmsg": self.errmsg}
        check_json = {
            "businessType": "epmpics",
            "method": "submitUpInfo",
            "jsonData": {
                "deptStr": post_dict["deptStr"],
                "areaStr": post_dict["areaStr"],
                "reportdate": round(time.time() * 1000),
                "customerid": post_dict["customerid"],
                "deptid": post_dict["deptStr"]["deptid"]
                if post_dict["deptStr"]
                else None,
                "source": "app",
                "templateid": post_dict["templateid"],
                "stuNo": post_dict["stuNo"],
                "username": post_dict["username"],
                "phonenum": post_dict["phonenum"] if post_dict["phonenum"] else self.user_info["phonenum"],
                "userid": post_dict["userid"],
                "updatainfo": post_dict["updatainfo"],
                "gpsType": 1,
                "token": self.token,
            },
        }
        result = self.base_check_in(check_json)
        if result:
            log.info("【第一类健康打卡成功】—— " + str(result))
            return {
                "status": 1,
                "res": result,
                "post_dict": post_dict,
                "check_json": check_json,
                "type": "healthy1",
            }
        else:
            log.error(self.errmsg + "（第一类健康打卡）")
            return {"status": 0, "errmsg": self.errmsg}
