import os
import json
import random
import win10toast
import time

from api.healthy1_check import get_healthy1_check_post_json, healthy1_check_in
from login import CampusLogin


toaster = win10toast.ToastNotifier()


def err(tittle: str, msg: str):
    while toaster.notification_active():
        time.sleep(0.5)
    toaster.show_toast(tittle,
                       msg,
                       icon_path=None,
                       duration=30,
                       threaded=True)
    pass


def random_deviceId() -> str:
    a = random.randint(0, 2**128)
    a = str(hex(a))
    return a[2: 2+8]+'-'+a[2+8: 2+8+4]+'-'+a[2+8+4: 2+8+4+4]+'-'+a[2+8+4+4: 2+8+4+4+4]+'-'+a[2+8+4+4: 2+8+4+4+12]


def update_json(path: str, jsonf: dict):
    with open(path, 'r+', encoding='utf-8') as file:
        file.seek(0, 0)
        file.truncate()
        file.write(json.dumps(jsonf, sort_keys=False,
                   indent=4, separators=(',', ': '), ensure_ascii=False))
    pass


def merge_post_json(dict1: dict, dict2: dict):
    for key, value in dict2.items():
        if value and key in dict1 and key != 'updatainfo':
            dict1[key] = value
        if key == 'updatainfo':
            dict3 = {}
            for i, j in enumerate(dict1['updatainfo']):
                dict3[j['propertyname']] = i
            for i in value:
                if i['propertyname'] in dict3:
                    dict1['updatainfo'][dict3[i['propertyname']]
                                        ]['value'] = i['value']
                    dict1['checkbox'][dict3[i['propertyname']]
                                      ]['value'] = i['value']


def load_conf(baseconf_path: str, plus_conf_path: str = ''):
    with open(baseconf_path) as f:
        a = json.load(f)
    if plus_conf_path:
        with open(plus_conf_path) as f:
            b = json.load(f)
        return a, b
    return a, {}


def get_token(user: dict, sms: bool = False, plus_conf: dict = {}):
    campus_login = CampusLogin(
        user['username'], user['device_id'], plus_info=plus_conf)
    if sms or not user['password']:
        campus_login.send_sms()
        sms = input('输入验证码：')
        token = campus_login.sms_login(sms)
    else:
        token = campus_login.pwd_login(user['password'])
    return token


def check_in(user: dict, user_plus: dict):
    try:
        if not user['device_id']:
            user['device_id'] = random_deviceId()
            user['token'] = get_token(user, sms=True, plus_conf=user_plus)
        elif not user['token']:
            user['token'] = get_token(user, plus_conf=user_plus)
        for _ in range(2):
            post_dict = get_healthy1_check_post_json(
                user['token'], "pneumonia")
            if post_dict == 1:
                user['token'] = get_token(user, plus_conf=user_plus)
                continue
            # 合并配置文件的打卡信息
            merge_post_json(post_dict, user_plus.get('postData', {}))
            res = healthy1_check_in(user, post_dict)
            if res['status'] == 2:
                user['token'] = get_token(user)
                continue
            break
    except Exception as e:
        err('完美校园', str(e.args))


def main_handler(*args, **kwargs):
    # 加载用户配置文件
    users, user_p = load_conf(
        kwargs['user_config_path'], kwargs['plus_config_path'])

    for user in users:
        if user['username']:
            check_in(user, user_p.get(user['username'], {}))
    # 更新配置
    update_json(kwargs['user_config_path'], users)
    pass


if __name__ == "__main__":
    user_config_path = os.path.join(
        os.path.dirname(__file__), 'conf', 'user.json')
    plus_config_path = os.path.join(
        os.path.dirname(__file__), 'conf', 'user_plus.json')
    main_handler(user_config_path=user_config_path,
                 plus_config_path=plus_config_path)
