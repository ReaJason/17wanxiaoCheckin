import json
import hashlib
import requests

from login import des_3
from login import rsa_encrypt as rsa
import login


class CampusLogin:
    __slots__ = ['login_info']

    def __init__(self, phone_num, device_id, plus_info={}):
        self.login_info = {
            "phoneNum": phone_num,
            "deviceId": device_id,
            "plus_info": plus_info
        }
        self.exchange_secret()

    def exchange_secret(self):
        rsa_keys = rsa.create_key_pair(1024)

        try:
            resp = requests.post(
                'https://app.17wanxiao.com/campus/cam_iface46/exchangeSecretkey.action',
                json={'key': rsa_keys[0]},
                headers=self.login_info['plus_info'].get('requestHeaders', {})
            )
            resp.raise_for_status()
            session_info = json.loads(rsa.rsa_decrypt(
                resp.text.encode(resp.apparent_encoding), rsa_keys[1]))
            self.login_info['sessionId'] = session_info['session']
            self.login_info['appKey'] = session_info['key'][:24]
        except Exception as e:
            raise Exception(*("密钥交换失败",) + e.args)

    def pwd_login(self, password):
        password_list = [des_3.des_3_encrypt(
            i, self.login_info['appKey'], '66666666') for i in password]
        login_args = {
            'userName': self.login_info['phoneNum'],
            'deviceId': self.login_info['deviceId'],
            'password': password_list,
            'requestMethod': 'cam_iface46/loginnew.action',
            'type': '1',
        }
        login_args.update(self.login_info['plus_info'].get('device_args',{}))
        upload_args = {
            'session': self.login_info['sessionId'],
            'data': des_3.object_encrypt(login_args, self.login_info['appKey'])
        }
        try:
            header = {'campusSign': hashlib.sha256(
                json.dumps(upload_args).encode('utf-8')).hexdigest()}
            header.update(self.login_info['plus_info'].get(
                'requestHeaders', {}))
            resp = requests.post(
                'https://app.17wanxiao.com/campus/cam_iface46/loginnew.action',
                headers=header,
                json=upload_args
            )
            resp.raise_for_status()
            resp = resp.json()
            if resp['result_']:
                return self.login_info['sessionId']
            raise Exception(resp['message_'])
        except Exception as e:
            raise Exception(*("密码登陆失败",) + e.args)

    def send_sms(self):
        send = {
            'mobile': self.login_info['phoneNum'],
            'deviceId': self.login_info['deviceId'],
            'requestMethod': "cam_iface46/gainMatrixCaptcha.action",
            'action': "registAndLogin",
            'type': "sms"
        }
        upload_args = {
            "session": self.login_info["sessionId"],
            "data": des_3.object_encrypt(send, self.login_info["appKey"])
        }
        try:
            header = {"campusSign": hashlib.sha256(
                json.dumps(upload_args).encode('utf-8')).hexdigest()}
            header.update(self.login_info['plus_info'].get(
                'requestHeaders', {}))
            resp = requests.post(
                "https://app.17wanxiao.com/campus/cam_iface46/gainMatrixCaptcha.action",
                headers=header,
                json=upload_args
            )
            resp.raise_for_status()
            resp = resp.json()
            """
            {"result_":true,"message_":"聚合验证码发送成功。","code_":0}
            """
            if resp['result_']:
                return {"msg": resp['message_']}
            raise Exception(resp)
        except Exception as e:
            raise Exception(*("验证码发送失败",) + e.args)

    def sms_login(self, sms):
        data = {
            'mobile': self.login_info['phoneNum'],
            'deviceId': self.login_info['deviceId'],
            'sms': sms,
            'type': '2',
        }
        data.update(self.login_info['plus_info'].get('device_args',{}))
        upload_args = {
            "session": self.login_info["sessionId"],
            "data": des_3.object_encrypt(data, self.login_info["appKey"])
        }
        try:
            header = {"campusSign": hashlib.sha256(
                json.dumps(upload_args).encode('utf-8')).hexdigest()}
            header.update(self.login_info['plus_info'].get(
                'requestHeaders', {}))
            resp = requests.post(
                "https://app.17wanxiao.com/campus/cam_iface46/registerUsersByTelAndLoginNew.action",
                headers=header,
                json=upload_args
            )
            resp.raise_for_status()
            resp = resp.json()

            if resp['result_']:
                return self.login_info['sessionId']
            raise Exception(resp['message_'])
        except Exception as e:
            raise Exception(*("验证码登陆失败",) + e.args)
