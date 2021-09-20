import json
import requests

from core.enum_api_url import WanXiaoServiceUrlEnum


class BaseCheck:
    def __init__(self, user_info, check_config_dict):
        self.check_config_dict = check_config_dict  # 配置文件中所配置的打卡参数
        self.user_info = user_info  # 个人信息
        self.token = user_info['token']
        self.headers = {
            "user-agent": "Mozilla/5.0 (Linux; Android 11; Redmi K20 Pro Build/RQ3A.210805.001.A1; wv) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/93.0.4577.62 Mobile "
            "Safari/537.36 Wanxiao/5.4.2"
        }
        self.errmsg = ""

    def get_last_check_json(self, fetch_post_dict):
        """
        获取完美校园记录的上一次的打卡参数
        :return:
        """
        try:
            res = requests.post(
                url=WanXiaoServiceUrlEnum.EPMPICS_URL.value,
                json=fetch_post_dict,
                headers=self.headers,
                timeout=10,
            ).json()
        except Exception as e:
            self.errmsg = f"【获取打卡参数失败】—— 错误原因：{e}"
            return None
        if res["code"] != "10000":
            """
            {'msg': '业务异常', 'code': '10007', 'data': '无法找到该机构的投票模板数据!'}
            """
            self.errmsg = f"【获取打卡参数失败】—— 错误原因：{res['data']}"
            return None
        data = json.loads(res["data"])
        post_dict = {
            "areaStr": data["areaStr"],
            "deptStr": data["deptStr"],
            "deptid": data["deptStr"]["deptid"] if data["deptStr"] else None,
            "customerid": data["customerid"],
            "userid": data["userid"],
            "username": data["username"],
            "stuNo": data["stuNo"],
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
                {
                    "description": i["decription"],
                    "value": i["value"],
                    "propertyname": i["propertyname"],
                }
                for i in data["cusTemplateRelations"]
            ],
        }
        return self.mix_last_check_json_and_config_dict(post_dict)

    def mix_last_check_json_and_config_dict(self, last_check_json):
        """
        将配置的打卡参数覆盖进获取到的打卡参数中
        :return:
        """
        for key, value in last_check_json.items():
            if value and key in self.check_config_dict and key != "updatainfo":
                last_check_json[key] = value
            if key == "updatainfo":
                dict3 = {}
                for i, j in enumerate(last_check_json["updatainfo"]):
                    dict3[j["propertyname"]] = i
                for i in value:
                    if i["propertyname"] in dict3:
                        last_check_json["updatainfo"][dict3[i["propertyname"]]][
                            "value"
                        ] = i["value"]
                        last_check_json["checkbox"][dict3[i["propertyname"]]][
                            "value"
                        ] = i["value"]
                        last_check_json["updatainfo_detail"][dict3[i["propertyname"]]][
                            "value"
                        ] = i["value"]
        return last_check_json

    def base_check_in(self, check_json):
        """
        打卡
        :return:
        """
        try:
            res = requests.post(
                url=WanXiaoServiceUrlEnum.EPMPICS_URL.value,
                json=check_json,
                headers=self.headers,
                timeout=10
            ).json()
        except Exception as e:
            self.errmsg = f"【打卡失败】—— 错误原因：{e}"
            return None
        if res["code"] == "10000":
            return res
        else:
            self.errmsg = f"【打卡失败】—— 错误原因：{res['data']}"
            return None
