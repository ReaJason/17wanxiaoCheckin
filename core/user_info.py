import requests

from login.campus import CampusLogin
from setting import log


class UserInfo:
    def __init__(self, username, password, device_id):
        self.password = password
        self.username = username
        self.device_id = device_id
        self.token = ""
        self.errmsg = ""

    def login(self):
        try:
            login_dict = CampusLogin(phone_num=self.username, device_id=self.device_id).pwd_login(self.password)
            if login_dict["status"]:
                self.token = login_dict["token"]
                return True
            else:
                self.errmsg = f"【完美校园登录失败】—— 错误原因：{self.username[:4]} {login_dict['errmsg']}"
                return False
        except Exception as e:
            self.errmsg = f"【完美校园登录失败】—— 错误原因：{self.username[:4]} {e}"
            return False

    def get_school_name(self):
        post_data = {"token": self.token, "method": "WX_BASE_INFO", "param": "%7B%7D"}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        try:
            res = requests.post(
                "https://server.59wanmei.com/YKT_Interface/xyk",
                data=post_data,
                headers=headers,
                timeout=10,
            )
            return res.json()["data"]["customerName"]
        except:
            return "霍格沃茨魔法学校"

    def get_user_info(self):
        if not self.login():
            log.error(self.errmsg)
            return {"status": 0, "errmsg": self.errmsg}
        data = {"appClassify": "DK", "token": self.token}
        try:
            res = requests.post(
                "https://reportedh5.17wanxiao.com/api/clock/school/getUserInfo",
                data=data,
                timeout=10,
            )
            user_info = res.json()["userInfo"]
            user_info["school"] = self.get_school_name()
            user_info['token'] = self.token
            user_info['phonenum'] = self.username
            user_info['password'] = self.password
            user_info['deviceid'] = self.device_id
            log.info(f"【获取个人信息成功】—— 欢迎来自『{user_info['school']}』的『*{user_info['username'][-1]}』朋友使用本脚本")
            return {"status": 1, "user_info": user_info}
        except Exception as e:
            self.errmsg = f"【获取个人信息失败】—— 错误原因：{e}"
            log.error(self.errmsg)
            return {"status": 0, "errmsg": self.errmsg}
