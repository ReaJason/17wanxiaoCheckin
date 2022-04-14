# 文件名：campus.py
# 创建日期：2020年09月13日09点44分
# 作者：Zhongbr
# 邮箱：zhongbr@icloud.com
"""
修改：ReaJason
修改日期：2021年2月1日
邮箱：reajason@163.com
博客：https://reajason.top
ChangeLog:
1、优化原作者写的账密登录方式和接口替换（server.17wanxiao.com -> app.17wanxiao.com）
2、增加短信登录方式
"""
import json
import hashlib
from math import radians
import requests
import urllib3

from login import des_3
from login import rsa_encrypt as rsa

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CampusLogin:

    def __init__(self, username, device_id, user_info,
                 #  app_version=10536101,
                 #  user_agent="Dalvik/2.1.0 (Linux; U; Android 11; Redmi K20 Pro Premium Edition Build/RKQ1.200826.002)",
                 #  phone_code="raphael", sys_type="android", sys_version="11", phone_model="Redmi K20 Pro Premium Edition"
                 ):

        # 初始化CampusLogin对象并交换密钥
        # :param phone_num: 完美校园登录账号（手机号）
        # :param device_id: 设备ID，模拟器IMEI或其他方式获取的可用于完美校园登录的ID
        # :param app_version: 完美校园app版本
        # :param user_agent: 账密登录时所用的用户代理
        # :param phone_code: 手机代号
        # :param sys_type: 系统类型，android，ipad，iphone
        # :param sys_version: 系统版本
        # :param phone_model: 手机机型

        self.userName = username
        self.deviceId = device_id
        self.sessionId = None
        self.appKey = None
        self.userInfo = {
            "wanxiaoVersion": user_info.get('wanxiaoVersion'),
            "userAgent": user_info.get('userAgent'),
            "shebeixinghao": user_info.get('shebeixinghao'),
            "systemType": user_info.get('systemType'),
            "telephoneInfo": user_info.get('telephoneInfo'),
            "telephoneModel": user_info.get('telephoneModel'),
            'appCode': user_info.get('appCode'),
            'netWork': user_info.get('netWork'),
            'qudao': user_info.get('qudao'),
            'yunyingshang': user_info.get('yunyingshang'),
        }
        self.__exchange_secret()

    def __exchange_secret(self):

        # 交换密钥
        # :return: if fail, raise error

        rsa_keys = rsa.create_key_pair(1024)
        resp = requests.post(
            'https://app.17wanxiao.com/campus/cam_iface46/exchangeSecretkey.action',
            headers={'User-Agent': self.userInfo['userAgent']},
            json={'key': rsa_keys[0]},
            # verify=False,
            timeout=30
        )
        resp.raise_for_status()
        session_info = json.loads(rsa.rsa_decrypt(
            resp.text.encode(resp.apparent_encoding), rsa_keys[1]))
        self.sessionId = session_info['session']
        self.appKey = session_info['key'][:24]

    def pwd_login(self, password):

        # 完美校园密码登录
        # :param password: 完美校园登录密码
        # :return: dict
        # if success：return {
        #                 "status": 1,
        #                 "token": token,
        #                 "msg": msg
        #             }
        # if fail：return {
        #              "status": 0,
        #              "errmsg": errmsg
        #          }

        password_list = [des_3.des_3_encrypt(
            i, self.appKey, '66666666') for i in password]
        login_args = {
            'userName': self.userName,
            'deviceId': self.deviceId,
            'password': password_list,
            'requestMethod': 'cam_iface46/loginnew.action',
            'type': '1',

            'appCode': self.userInfo['appCode'],
            'netWork': self.userInfo['netWork'],
            'qudao': self.userInfo['qudao'],
            'yunyingshang': self.userInfo['yunyingshang'],
            'shebeixinghao': self.userInfo['shebeixinghao'],
            'systemType': self.userInfo['systemType'],
            'telephoneInfo': self.userInfo['telephoneInfo'],
            'telephoneModel': self.userInfo['telephoneModel'],
            'wanxiaoVersion': self.userInfo['wanxiaoVersion'],
        }
        upload_args = {
            'session': self.sessionId,
            'data': des_3.object_encrypt(login_args, self.appKey)
        }
        resp = requests.post(
            'https://app.17wanxiao.com/campus/cam_iface46/loginnew.action',
            headers={'campusSign': hashlib.sha256(
                json.dumps(upload_args).encode('utf-8')).hexdigest(),
                'User-Agent': self.userInfo['userAgent']},
            json=upload_args,
            # verify=False,
            timeout=30,
        )
        resp.raise_for_status()
        resp = resp.json()
        # {'result_': True, 'data': '........', 'message_': '登录成功', 'code_': '0'}
        # {'result_': False, 'message_': '该手机号未注册完美校园', 'code_': '4'}
        # {'result_': False, 'message_': '您正在新设备上使用完美校园，请使用验证码进行验证登录', 'code_': '5'}
        # {'result_': False, 'message_': '密码错误,您还有5次机会!', 'code_': '5'}
        if resp['result_']:
            return self.sessionId
        else:
            raise Exception('登陆失败！', resp)
        # return {"status": 0, "errmsg": resp['message_']}

    def send_sms(self):
        # 发送短信
        # :return: dict
        # if success：return {
        #                 "status": 1,
        #                 "msg": msg
        #             }
        # if fail：return {
        #              "status": 0,
        #              "errmsg": errmsg
        #          }
        send = {
            'action': "registAndLogin",
            'deviceId': self.deviceId,
            'mobile': self.userName,
            'requestMethod': "cam_iface46/gainMatrixCaptcha.action",
            'type': "sms",
        }
        upload_args = {
            "session": self.sessionId,
            "data": des_3.object_encrypt(send, self.appKey)
        }
        resp = requests.post(
            "https://app.17wanxiao.com/campus/cam_iface46/gainMatrixCaptcha.action",
            headers={"campusSign": hashlib.sha256(
                json.dumps(upload_args).encode('utf-8')).hexdigest(),
                'User-Agent': self.userInfo['userAgent']},
            json=upload_args,
            # verify=False,
            timeout=30
        )
        resp.raise_for_status()
        resp = resp.json()
        """
        {"result_":true,"message_":"聚合验证码发送成功。","code_":0}
        """
        if not resp['result_']:
            raise Exception('验证码发送失败',resp)

    def sms_login(self, sms):

        # 短信登录
        # :param sms: 收到的验证码
        # :return: dict
        # if success：return {
        #                 "status": 1,
        #                 "token": token,
        #                 "msg": msg
        #             }
        # if fail：return {
        #              "status": 0,
        #              "errmsg": errmsg
        #          }

        data = {
            'mobile': self.userName,
            'deviceId': self.deviceId,
            'sms': sms,
            'requestMethod': "cam_iface46/registerUsersByTelAndLoginNew.action",
            'type': '2',

            'appCode': self.userInfo['appCode'],
            'netWork': self.userInfo['netWork'],
            'qudao': self.userInfo['qudao'],
            'shebeixinghao': self.userInfo['shebeixinghao'],
            'systemType': self.userInfo['systemType'],
            'telephoneInfo': self.userInfo['telephoneInfo'],
            'telephoneModel': self.userInfo['telephoneModel'],
            'wanxiaoVersion': self.userInfo['wanxiaoVersion'],
        }
        upload_args = {
            "session": self.sessionId,
            "data": des_3.object_encrypt(data, self.appKey)
        }
        resp = requests.post(
            "https://app.17wanxiao.com/campus/cam_iface46/registerUsersByTelAndLoginNew.action",
            headers={"campusSign": hashlib.sha256(
                json.dumps(upload_args).encode('utf-8')).hexdigest(),
                'User-Agent': self.userInfo['userAgent']},
            json=upload_args,
            # verify=False,
            timeout=30
        )
        resp.raise_for_status()
        resp = resp.json()

        # {"result_":true,"data":"******","message_":"登录成功","code_":"0"}
        # {"result_":false,"message_":"短信验证码错误","code_":"6"}

        if resp['result_']:
            return self.sessionId
        else:
            raise Exception('登陆失败', resp['message_'])
