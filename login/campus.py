import random
import json
import hashlib
import requests
import urllib3
import logging

from login import des_3
from login import rsa_encrypt as rsa

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CampusCard:
    """
    完美校园APP
    初始化时需要传入手机号码、密码、用户信息（如果有）
    """
    data = None

    def __init__(self, phone, password):
        """
        初始化一卡通类
        :param phone: 完美校园账号
        :param password: 完美校园密码
        :param user_info: 已登录的虚拟设备
        """
        self.user_info = self.__create_blank_user__()
        if self.user_info['exchangeFlag']:
            self.exchange_secret()
            self.login(phone, password)

    @staticmethod
    def __create_blank_user__():
        """
        当传入的已登录设备信息不可用时，虚拟一个空的未登录设备
        :return: 空设备信息
        """
        rsa_keys = rsa.create_key_pair(1024)
        return {
            'appKey': '',
            'sessionId': '',
            'exchangeFlag': True,
            'login': False,
            'serverPublicKey': '',
            'deviceId': str(random.randint(999999999999999, 9999999999999999)),
            'wanxiaoVersion': 10462101,
            'rsaKey': {
                'private': rsa_keys[1],
                'public': rsa_keys[0]
            }
        }

    def exchange_secret(self):
        """
        与完美校园服务器交换RSA加密的公钥，并取得sessionId
        :return:
        """
        resp = requests.post(
            "https://server.17wanxiao.com/campus/cam_iface46/exchangeSecretkey.action",
            headers={
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 5.1.1; HUAWEI MLA-AL10 Build/HUAWEIMLA-AL10)",
            },
            json={
                "key": self.user_info["rsaKey"]["public"]
            },
            verify=False
        )
        session_info = json.loads(
            rsa.rsa_decrypt(resp.text.encode(resp.apparent_encoding), self.user_info["rsaKey"]["private"])
        )
        self.user_info["sessionId"] = session_info["session"]
        self.user_info["appKey"] = session_info["key"][:24]

    def login(self, phone, password):
        """
        使用账号密码登录完美校园APP
        :param phone: 完美校园APP绑定的手机号码
        :param password: 完美校园密码
        :return:
        """
        password_list = []
        for i in password:
            password_list.append(des_3.des_3_encrypt(i, self.user_info["appKey"], "66666666"))
        login_args = {
            "appCode": "M002",
            "deviceId": self.user_info["deviceId"],
            "netWork": "wifi",
            "password": password_list,
            "qudao": "guanwang",
            "requestMethod": "cam_iface46/loginnew.action",
            "shebeixinghao": "MLA-AL10",
            "systemType": "android",
            "telephoneInfo": "5.1.1",
            "telephoneModel": "HUAWEI MLA-AL10",
            "type": "1",
            "userName": phone,
            "wanxiaoVersion": 10462101,
            "yunyingshang": "07"
        }
        upload_args = {
            "session": self.user_info["sessionId"],
            "data": des_3.object_encrypt(login_args, self.user_info["appKey"])
        }
        resp = requests.post(
            "https://server.17wanxiao.com/campus/cam_iface46/loginnew.action",
            headers={"campusSign": hashlib.sha256(json.dumps(upload_args).encode('utf-8')).hexdigest()},
            json=upload_args,
            verify=False
        ).json()
        if resp["result_"]:
            logging.info(f"{phone}：{resp['message_']}")
            self.data = resp["data"]
            self.user_info["login"] = True
            self.user_info["exchangeFlag"] = False
        else:
            logging.warning(f"{phone}：{resp['message_']}")
