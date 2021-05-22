import os
import time

from api.campus_check import get_id_list_v1, get_id_list_v2, get_customer_type_id, get_campus_check_post, \
    campus_check_in
from api.healthy1_check import get_healthy1_check_post_json, healthy1_check_in
from api.healthy2_check import get_healthy2_check_posh_json, healthy2_check_in
from api.user_info import get_user_info
from api.wanxiao_push import wanxiao_qmsg_push, wanxiao_server_push, wanxiao_email_push, wanxiao_pipe_push, \
    wanxiao_wechat_enterprise_push
from api.ykt_score import get_score_list, get_active_score, get_task_list, get_article_id, get_all_score, \
    get_article_score, get_class_score, ykt_check_in
from login import CampusLogin
from setting import log
from utils.config import load_config


def get_token(username, password, device_id):
    try:
        campus_login = CampusLogin(phone_num=username, device_id=device_id)
    except Exception as e:
        log.warning(e)
        return None
    login_dict = campus_login.pwd_login(password)
    if login_dict["status"]:
        log.info(f"{username[:4]}，{login_dict['msg']}")
        return login_dict["token"]
    else:
        log.warning(f"{username[:4]}，{login_dict['errmsg']}")
        return None


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
                    dict1['updatainfo'][dict3[i['propertyname']]]['value'] = i['value']
                    dict1['checkbox'][dict3[i['propertyname']]]['value'] = i['value']


def info_push(push_dict, raw_info):
    push_funcs = {
        "email": wanxiao_email_push,
        "wechat": wanxiao_server_push,
        "qmsg": wanxiao_qmsg_push,
        "pipehub": wanxiao_pipe_push,
        "wechat_enterprise": wanxiao_wechat_enterprise_push
    }
    
    push_raw_info = {
        "check_info_list": raw_info
    }
    
    for push_name, push_func in push_funcs.items():
        enable = push_dict[push_name]["enable"]
        if not enable:
            pass
        else:
            del push_dict[push_name]["enable"]
            push_dict[push_name].update(push_raw_info)
            params_dict = push_dict[push_name]
            push_res = push_func(**params_dict)
            if push_res['status']:
                log.info(push_res["msg"])
            else:
                log.warning(push_res["errmsg"])


def check_in(user):
    check_dict_list = []
    
    # 登录获取token用于打卡
    token = get_token(user['phone'], user['password'], user['device_id'])
    
    if not token:
        errmsg = f"{user['phone'][:4]}，获取token失败，打卡失败"
        log.warning(errmsg)
        check_dict_list.append({"status": 0, "errmsg": errmsg})
        return check_dict_list
    
    # 获取个人信息
    user_info = get_user_info(token)
    if not user_info:
        errmsg = f"{user['phone'][:4]}，获取个人信息失败，打卡失败"
        log.warning(errmsg)
        check_dict_list.append({"status": 0, "errmsg": errmsg})
        return check_dict_list
    log.info(f'{user_info["username"][0]}-{user_info["school"]}，获取个人信息成功')
    
    healthy1_check_config = user['healthy_checkin']['one_check']
    healthy2_check_config = user['healthy_checkin']['two_check']
    if healthy1_check_config['enable']:
        # 第一类健康打卡
        
        # 获取第一类健康打卡的参数
        post_dict = get_healthy1_check_post_json(token)
        
        # 合并配置文件的打卡信息
        merge_post_json(post_dict, healthy1_check_config['post_json'])
        
        healthy1_check_dict = healthy1_check_in(token, user['phone'], post_dict)
        check_dict_list.append(healthy1_check_dict)
    elif healthy2_check_config['enable']:
        # 第二类健康打卡
        
        # 获取第二类健康打卡参数
        post_dict = get_healthy2_check_posh_json(token)
        
        # 合并配置文件的打卡信息
        if not healthy2_check_config['post_json']['latitude'] and not healthy2_check_config['post_json']['longitude']:
            post_dict['latitude'] = ""
            post_dict['longitude'] = ""
            log.info('当前打卡未设置经纬度，后台会将此次打卡计为手动打卡（学校没做要求可不管）')
        for i, j in healthy2_check_config['post_json'].items():
            if j:
                post_dict[i] = j
        healthy2_check_dict = healthy2_check_in(token, user_info["customerId"], post_dict)
        
        check_dict_list.append(healthy2_check_dict)
    else:
        log.info('当前并未配置健康打卡方式，暂不进行打卡操作')
    
    # 校内打卡
    campus_check_config = user['campus_checkin']
    if not campus_check_config['enable']:
        log.info('当前并未开启校内打卡，暂不进行打卡操作')
    else:
        # 获取校内打卡ID
        custom_type_id = user_info.get('customerAppTypeId', get_customer_type_id(token))
        if custom_type_id:
            id_list = get_id_list_v2(token, custom_type_id)
        else:
            id_list = get_id_list_v1(token)
        
        if not id_list:
            log.warning('当前未获取到校内打卡ID，请尝试重新运行，如仍未获取到，请反馈')
            return check_dict_list
        for index, i in enumerate(id_list):
            start_end = f'{i["templateid"]} ({i.get("startTime", "")}-{i.get("endTime", "")})'
            log.info(f"{start_end:-^40}")
            
            # 获取校内打卡参数
            campus_dict = get_campus_check_post(
                template_id=i['templateid'],
                custom_rule_id=i['id'],
                stu_num=user_info['stuNo'],
                token=token
            )
            # 合并配置文件的打卡信息
            merge_post_json(campus_dict, campus_check_config['post_json'])
            
            # 校内打卡
            campus_check_dict = campus_check_in(user['phone'], token, campus_dict, i['id'])
            check_dict_list.append(campus_check_dict)
            log.info("-" * 40)
    
    # 粮票收集
    if user['ykt_score']:
        ykt_check_in(token)
        get_all_score(token)
        task_list = get_task_list(token)
        for task in task_list:
            if task['name'] == '校园头条':
                if not task['finished']:
                    article_id = get_article_id(token)
                    for _ in range(8):
                        time.sleep(1)
                        get_article_score(token, article_id)
                else:
                    log.info("校园头条任务已完成")
            get_all_score(token)
            if task['name'] == '查看课表':
                if not task['finished']:
                    get_class_score(token)
                else:
                    log.info("查看课表任务已完成")
        # 获取活跃奖励
        get_active_score(token, get_score_list(token)['active'][0])
        
        # 获取其他奖励
        get_all_score(token)
        
    return check_dict_list


def main_handler(*args, **kwargs):
    # 推送数据
    raw_info = []
    
    # 加载用户配置文件
    user_config_dict = load_config(kwargs['user_config_path'])
    for user_config in user_config_dict:
        if not user_config['phone']:
            continue
        log.info(user_config['welcome'])
        
        # 单人打卡
        check_dict = check_in(user_config)
        # 单人推送
        info_push(user_config['push'], check_dict)
        raw_info.extend(check_dict)
    
    # 统一推送
    all_push_config = load_config(kwargs['push_config_path'])
    info_push(all_push_config, raw_info)


if __name__ == "__main__":
    user_config_path = os.path.join(os.path.dirname(__file__), 'conf', 'user.json')
    push_config_path = os.path.join(os.path.dirname(__file__), 'conf', 'push.json')
    main_handler(user_config_path=user_config_path, push_config_path=push_config_path)
