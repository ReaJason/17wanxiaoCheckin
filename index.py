from cgitb import handler
from io import StringIO
import os
import traceback
import logging

import json5
import json

from random import randint
from requests.exceptions import RequestException

from api import *
from login import CampusLogin
from utils.config import load_config
from utils.Errors import *


def update_json(path: str, jsonf: dict):
    with open(path, 'r+', encoding='utf-8') as file:
        file.seek(0, 0)
        file.truncate()
        file.write(json.dumps(jsonf, sort_keys=False,
                   indent=4, separators=(',', ': '), ensure_ascii=False))
    pass


def init_log(level=logging.INFO) -> None:
    logging.basicConfig(
        format='%(asctime)s - [%(levelname)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def random_deviceId() -> str:
    a = randint(0, 2**128)
    a = str(hex(a))
    return a[2: 2+8]+'-'+a[2+8: 2+8+4]+'-'+a[2+8+4: 2+8+4+4]+'-'+a[2+8+4+4: 2+8+4+4+4]+'-'+a[2+8+4+4: 2+8+4+4+12]


def get_token(user, user_info) -> None:
    log = logging.getLogger('main.'+user['username'])
    # token将被写入user
    campus_login = CampusLogin(
        user['username'], user['device_id'], user_info=user_info)
    if user['sms_login']:
        log.info('正在使用短信验证码登陆')
        campus_login.send_sms()
        sms = input('输入验证码：')
        user['token'] = campus_login.sms_login(sms)
    else:
        log.info('正在使用密码登陆')
        if not user['password']:
            raise Exception('没有密码！')
        user['token'] = campus_login.pwd_login(user['password'])


def merge_post_json(dict1, dict2):
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


def info_push(push_conf, msg):
    log = logging.getLogger('main')

    push_funcs = {
        "email": wanxiao_email_push,
        "wechat": wanxiao_server_push,
        "qmsg": wanxiao_qmsg_push,
        "pipehub": wanxiao_pipe_push,
        "wechat_enterprise": wanxiao_wechat_enterprise_push,
        "bark": wanxiao_bark_push
    }

    push_raw_info = {
        "msg": msg
    }

    for push_name, push_func in push_funcs.items():
        if not push_conf.get(push_name):
            pass
        else:
            push_conf[push_name].update(push_raw_info)
            params_dict = push_conf[push_name]
            push_res = push_func(**params_dict)
            if push_res['status']:
                log.info('推送成功'+push_res["msg"])
            else:
                log.warning('未能成功推送！'+push_res["errmsg"])


def check_in(user: dict, user_info: dict, check_info: dict):
    log = logging.getLogger('main.'+user['username'])

    lf = 0
    nf = 0
    cf = False
    while True:
        # 登录获取token用于打卡
        if not user['token']:
            get_token(user, user_info)
        else:
            log.info('使用了上次的token')

        try:
            if user['healthy1_checkin']:
                log.info('正在执行第一类健康打卡')
                cf = True

                # 第一类健康打卡

                # 获取第一类健康打卡的参数
                post_dict = get_healthy1_check_post_json(
                    user, check_info.get('templateid', "pneumonia"))

                # 合并配置文件的打卡信息
                if check_info.get('one_check'):
                    merge_post_json(
                        post_dict, check_info['one_check']['post_json'])

                healthy1_check_in(user, post_dict)
            if user['healthy2_checkin']:
                log.info('正在执行第二类健康打卡')
                cf = True

                # 第二类健康打卡

                # 获取第二类健康打卡参数
                post_dict = get_healthy2_check_posh_json(user['token'])

                # 合并配置文件的打卡信息
                if not check_info['two_check']['post_json']['latitude'] and not check_info['two_check']['post_json']['longitude']:
                    post_dict['latitude'] = ""
                    post_dict['longitude'] = ""
                    log.info('当前打卡未设置经纬度，后台会将此次打卡计为手动打卡（学校没做要求可不管）')
                for i, j in check_info['two_check']['post_json'].items():
                    if j:
                        post_dict[i] = j
                healthy2_check_in(
                    user['token'], user_info["customerId"], post_dict)

            # 校内打卡

            if user['campus_checkin']:
                log.info('正在执行校内打卡')
                cf = True

                # 获取校内打卡ID
                custom_type_id = user_info.get(
                    'customerAppTypeId', get_customer_type_id(user['token']))
                if custom_type_id:
                    id_list = get_id_list_v2(user, custom_type_id)
                else:
                    id_list = get_id_list_v1(user)

                if not id_list:
                    log.warning('当前未获取到校内打卡ID，请尝试重新运行，如仍未获取到，请反馈')
                    return  # check_dict_list
                for index, i in enumerate(id_list):
                    start_end = f'{i["templateid"]} ({i.get("startTime", "")}-{i.get("endTime", "")})'
                    log.info(f"{start_end:-^40}")

                    # 获取校内打卡参数
                    campus_dict = get_campus_check_post(
                        template_id=i['templateid'],
                        custom_rule_id=i['id'],
                        stu_num=user_info['stuNo'],
                        token=user['token'],
                        log=log
                    )
                    # 合并配置文件的打卡信息
                    merge_post_json(
                        campus_dict, check_info['campus_checkin']['post_json'])

                    # 校内打卡
                    campus_check_dict = campus_check_in(
                        user['username'], user['token'], campus_dict, i['id'], log=log)

            # # 粮票收集
            # if user['ykt_score']:
            #     ykt_check_in(token)
            #     get_all_score(token)
            #     task_list = get_task_list(token)
            #     for task in task_list:
            #         if task['name'] == '校园头条':
            #             if not task['finished']:
            #                 article_id = get_article_id(token)
            #                 for _ in range(8):
            #                     time.sleep(1)
            #                     get_article_score(token, article_id)
            #             else:
            #                 log.info("校园头条任务已完成")
            #         get_all_score(token)
            #         if task['name'] == '查看课表':
            #             if not task['finished']:
            #                 get_class_score(token)
            #             else:
            #                 log.info("查看课表任务已完成")
            #     # 获取活跃奖励
            #     get_active_score(token, get_score_list(token)['active'][0])

            #     # 获取其他奖励
            #     get_all_score(token)

            # return check_dict_list

        except NotLoginError:
            if lf == 1:
                log.error("未知错误！\n" + traceback.format_exc())
                break
            log.info('token失效')
            lf += 1
            user['token'] = ''
            continue
        except RequestException as e:
            if nf >= 3:
                log.error("网络错误！\n" + traceback.format_exc())
                break
            log.info("网络请求失败, 正在重试\n" + repr(e))
            nf += 1
            continue
        except:
            log.error('发生了一个错误\n' + traceback.format_exc())
        if not cf:
            log.warning("未配置任何打卡项目！")
        break


def main_handler(*args, **kwargs):
    # 初始化日志
    init_log()
    log = logging.getLogger('main')
    log.setLevel(logging.DEBUG)
    pushbuf = StringIO()
    loghandler = logging.StreamHandler(pushbuf)
    log.addHandler(loghandler)
    logging.getLogger('requests').setLevel(logging.WARNING)
    # 加载用户配置文件
    try:
        user_config_path = kwargs.get('user_config_path', './conf/user.jsonc')
        user_info_path = kwargs.get('user_info_path', './conf/user_info.jsonc')
        check_info_path = kwargs.get(
            'check_info_path', './conf/check_info.jsonc')
        push_config_path = kwargs.get('push_config_path', './conf/push.jsonc')
        user_dict: dict = load_config(user_config_path)
        user_info_dict: dict = load_config(user_info_path)
        check_info_dict: dict = load_config(check_info_path)
        push_dict: dict = load_config(push_config_path)
    except:
        log.critical("配置文件加载失败！\n"+traceback.format_exc())
        exit(1)

    for user in user_dict:
        if not user['username']:
            continue

        # 初始化日志
        userlog = logging.getLogger('main.'+user['username'])
        userPushBuf = StringIO()
        userLogHandler = logging.StreamHandler(userPushBuf)
        userlog.addHandler(userLogHandler)
        userlog.info('用户'+user['username']+':')

        if not user['device_id']:
            userlog.info('生成了新的device_id')
            user['device_id'] = random_deviceId()
        # 单人打卡
        check_in(user,
                 user_info_dict.get(user['username'], {}),
                 check_info_dict.get(user['username'], {}))
        # 单人推送
        if push_dict.get(user['username']):
            info_push(push_dict.get(user['username']), userPushBuf.getvalue())
        else:
            log.info('当前用户未配置推送')

    # 统一推送
    update_json(user_config_path, user_dict)
    log.info('用户数据更新成功')
    info_push(push_dict['default'], pushbuf.getvalue())


if __name__ == "__main__":

    user_config_path = os.path.join(
        os.path.dirname(__file__), 'conf', 'user.jsonc')
    user_info_path = os.path.join(
        os.path.dirname(__file__), 'conf', 'user_info.jsonc')
    check_info_path = os.path.join(
        os.path.dirname(__file__), 'conf', 'check_info.jsonc')
    push_config_path = os.path.join(
        os.path.dirname(__file__), 'conf', 'push.jsonc')

    main_handler(user_config_path=user_config_path,
                 user_info_path=user_info_path,
                 check_info_path=check_info_path,
                 push_config_path=push_config_path)
