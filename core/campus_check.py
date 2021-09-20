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
import requests
from setting import log
from core.base_check import BaseCheck
from core.enum_api_url import WanXiaoServiceUrlEnum


class CampusCheck(BaseCheck):
    def __init__(self, user_info, check_config_dict):
        super().__init__(user_info, check_config_dict)

    def get_id_list_v1(self):
        """
        通过校内模板id获取校内打卡具体的每个时间段id（初版,暂留）
        :return: 返回校内打卡id列表
        """
        post_data = {"appClassify": "DK", "token": self.token}
        try:
            res = requests.post(
                WanXiaoServiceUrlEnum.GET_CAMPUS_CHECK_ID_LIST1_URL.value,
                headers=self.headers,
                data=post_data,
                timeout=10,
            ).json()
            if res.json()["appList"]:
                app_list = (
                    res["appList"][-1]["customerAppTypeRuleList"]
                    if res["appList"][-1]["customerAppTypeRuleList"]
                    else res["appList"][0]["customerAppTypeRuleList"]
                )
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
        except Exception as e:
            self.errmsg = f"【获取校内单个模板 ID 失败】—— 错误原因：{e}"
            return None

    def get_id_list_v2(self, custom_type_id):
        post_data = {
            "customerAppTypeId": custom_type_id,
            "longitude": "",
            "latitude": "",
            "token": self.token,
        }
        try:
            res = requests.post(
                WanXiaoServiceUrlEnum.GET_CAMPUS_CHECK_ID_LIST1_URL.value,
                data=post_data,
                headers=self.headers,
                timeout=10,
            )
            return res.json()["customerAppTypeDto"]["ruleList"]
        except Exception as e:
            self.errmsg = f"【获取校内单个模板 ID 失败】—— 错误原因：{e}"
            return None

    def get_customer_type_id(self):
        post_data = {"appClassify": "DK", "token": self.token}
        try:
            res = requests.post(
                WanXiaoServiceUrlEnum.GET_CAMPUS_CHECK_ID_LIST2_URL.value,
                headers=self.headers,
                data=post_data,
                timeout=10,
            ).json()
            for app in res["appList"]:
                if "校内" in app["name"]:
                    return app["id"]
        except Exception as e:
            self.errmsg = f"【获取校内打卡总模板 ID 失败】—— 错误原因：{e}"
            return None

    def check_in(self):
        check_in_result_list = []
        custom_type_id = self.user_info.get(
            "customerAppTypeId", self.get_customer_type_id()
        )
        if custom_type_id:
            id_list = self.get_id_list_v2(custom_type_id)
        else:
            id_list = self.get_id_list_v1()
        if not id_list:
            self.errmsg += "当前未获取到校内打卡ID，请尝试重新运行，如仍未获取到，请反馈"
            log.error(self.errmsg)
            check_in_result_list.append({"status": 0, "errmsg": self.errmsg})
        log.debug(id_list)
        for index, i in enumerate(id_list):
            # 获取校内打卡参数
            campus_check_post_json = {
                "businessType": "epmpics",
                "jsonData": {
                    "templateid": i["templateid"],
                    "customerAppTypeRuleId": i["id"],
                    "stuNo": self.user_info["stuNo"],
                    "token": self.token,
                },
                "method": "userComeAppSchool",
                "token": self.token,
            }
            post_dict = self.get_last_check_json(campus_check_post_json)
            if not post_dict:
                log.error(self.errmsg)
                check_in_result_list.append({"status": 0, "errmsg": self.errmsg})
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
                    "phonenum": self.user_info['phonenum'],
                    "userid": post_dict["userid"],
                    "updatainfo": post_dict["updatainfo"],
                    "customerAppTypeRuleId": i["id"],
                    "clockState": 0,
                    "token": self.token,
                },
                "token": self.token,
            }
            log.debug(check_json)
            result = self.base_check_in(check_json)
            if result:
                log.info("【校内打卡成功】—— " + str(result))
                check_in_result_list.append(
                    {
                        "status": 1,
                        "res": result,
                        "post_dict": post_dict,
                        "check_json": check_json,
                        "type": post_dict["templateid"],
                    }
                )
            else:
                log.error(self.errmsg + "（校内打卡）")
                check_in_result_list.append({"status": 0, "errmsg": self.errmsg})
        return check_in_result_list
