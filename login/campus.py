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
    __slots__ = ['phone', 'password', 'user_info']

    def __init__(self, phone, password):
        '''
        初始化一卡通类
        :param phone: 完美校园账号
        :param password: 完美校园密码
        '''
        self.phone = phone
        self.password = password
        self.user_info = self.create_blank_user()
        flag = self.exchange_secret()
        if flag:
            self.login()

    def create_blank_user(self):
        '''
        当传入的已登录设备信息不可用时，虚拟一个空的未登录设备
        :return: 空设备信息
        '''
        rsa_keys = rsa.create_key_pair(1024)
        return {
            'appKey': '',
            'sessionId': '',
            'exchangeFlag': True,
            'login': False,
            'serverPublicKey': '',
            'deviceId': str(random.randint(999999999999999, 9999999999999999)),
            'wanxiaoVersion': 10531102,
            'rsaKey': {
                'private': rsa_keys[1],
                'public': rsa_keys[0]
            }
        }

    def exchange_secret(self):
        '''
        与完美校园服务器交换RSA加密的公钥，并取得sessionId
        :return:
        '''
        try:
            resp = requests.post(
                'https://app.17wanxiao.com/campus/cam_iface46/exchangeSecretkey.action',
                headers={
                    'User-Agent': 'NCP/5.3.1 (iPhone; iOS 13.5; Scale/2.00)',
                },
                json={
                    'key': self.user_info['rsaKey']['public']
                },
                verify=False,
                timeout=30
            )
            session_info = json.loads(
                rsa.rsa_decrypt(resp.text.encode(resp.apparent_encoding), self.user_info['rsaKey']['private'])
            )
            self.user_info['sessionId'] = session_info['session']
            self.user_info['appKey'] = session_info['key'][:24]
            return True
        except Exception as e:
            logging.warning(e)
            return False

    def login(self):
        '''
        使用账号密码登录完美校园APP
        :param phone: 完美校园APP绑定的手机号码
        :param password: 完美校园密码
        :return:
        '''
        password_list = []
        for i in self.password:
            password_list.append(des_3.des_3_encrypt(i, self.user_info['appKey'], '66666666'))
        login_args = {
            'appCode': 'M002',
            'deviceId': self.user_info['deviceId'],
            'netWork': 'wifi',
            'password': password_list,
            'qudao': 'guanwang',
            'requestMethod': 'cam_iface46/loginnew.action',
            'shebeixinghao': 'iPhone12',
            'systemType': 'iOS',
            'telephoneInfo': '13.5',
            'telephoneModel': 'iPhone',
            'type': '1',
            'userName': self.phone,
            'wanxiaoVersion': 10531102,
            'yunyingshang': '07'
        }
        upload_args = {
            'session': self.user_info['sessionId'],
            'data': des_3.object_encrypt(login_args, self.user_info['appKey'])
        }
        try:
            resp = requests.post(
                'https://app.17wanxiao.com/campus/cam_iface46/loginnew.action',
                headers={'campusSign': hashlib.sha256(json.dumps(upload_args).encode('utf-8')).hexdigest()},
                json=upload_args,
                verify=False,
                timeout=30,
            ).json()
            if resp['result_']:
                logging.info(f'{self.phone[:4]}：{resp["message_"]}')
                self.user_info['login'] = True
                self.user_info['exchangeFlag'] = False
            else:
                logging.info(f'{self.phone[:4]}：{resp["message_"]}')
            return resp['result_']
        except Exception as e:
            logging.warning(e)
