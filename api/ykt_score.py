"""
粮票获取
@create：2021/04/24
@filename：ykt_score.py
@author：ReaJason
@email_addr：reajason@163.com
@blog_website：https://reajason.top
@last_modify：2021/04/26
"""
import requests

from setting import log


def get_task_list(token):
    data = f"token={token}" \
           "&method=makeScoreTask" \
           f"&param=%7B%22token%22%3A%22{token}%22%2C%22qudao%22%3A%220%22%2C%22device%22%3A%221%22%7D"
    headers = {
        'content-type': 'application/x-www-form-urlencoded'
    }
    try:
        res = requests.post("https://server.17wanxiao.com/YKT_Interface/score", data=data, headers=headers).json()
        if res['result_']:
            return [{"name": task["name"], "finished": task["finished"]} for task in res['data']['taskList']]
    except Exception as e:
        log.warning(f'{e.__class__}:{e} 获取任务列表失败')
        return None


def ykt_check_in(token):
    """
    获取签到粮票
    :param token:
    """
    data = f"token={token}" \
           "&method=WX_h5signIn" \
           f"&param=%7B%22token%22%3A%22{token}%22%7D"
    headers = {
        'content-type': 'application/x-www-form-urlencoded'
    }
    try:
        res = requests.post("https://server.17wanxiao.com/YKT_Interface/xyk", data=data, headers=headers).json()
        log.info(res['data']['alertMessage'])
    except:
        log.warning("签到失败")


def get_article_id(token):
    """
    获取文章 id
    :return:
    """
    post_json = {
        "typeCode": "campusNews",
        "pageSize": 10,
        "pageNo": 1,
        "token": token
    }
    try:
        res = requests.post("https://information.17wanxiao.com/cms/api/info/list", json=post_json).json()
        return res['data']['rows'][0]['id']
    except:
        return None


def get_article_score(token, article_id):
    """
    查看文章
    :param article_id:
    :param token:
    :return:
    """
    data = {
        "id": article_id,
        "token": token
    }
    try:
        res = requests.post("https://information.17wanxiao.com/cms/api/info/detail", data=data).json()
        if res['result_']:
            # log.info('查看文章成功')
            pass
        else:
            log.warning(f'查看文章失败，{res}')
    except Exception as e:
        log.warning(f'查看文章失败，{e}')


def get_talents_token(token):
    try:
        res = requests.get(f"https://api.xiaozhao365.com/operation/pub/iface/userInfo?token={token}").json()
        return res['userInfo']['talents_token']
    except:
        return None


def get_class_score(token):
    post_json = {"token": token, "command": "CURRI_SERVER.WEEK_CURRI", "week": ""}
    try:
        res = requests.post("https://course.59wanmei.com/campus-score/curriculum/_iface/server/invokInfo.action",
                            json=post_json)
        if res.status_code == 200:
            log.info("查看课表成功")
        else:
            log.warning("查看课表失败")
    except Exception as e:
        log.warning(f"{e} 查看课表失败")


def get_score_list(token):
    """
    获取所有的奖励数据
    :param token
    :return: dict
    """
    data = f"token={token}" \
           "&method=gainScoreCircleList" \
           f"&param=%7B%22token%22%3A%22{token}%22%7D"
    headers = {
        'content-type': 'application/x-www-form-urlencoded'
    }
    try:
        res = requests.post("https://server.17wanxiao.com/YKT_Interface/score", data=data, headers=headers).json()
        return {
            'sign': res['signCircleStatus'],
            'active': res['activeCircleList'],
            'circle': res['circleList']
        }
    except:
        return None


def get_active_score(token, active_dict):
    """
    获取活动奖励
    """
    data = f"token={token}" \
           "&method=gainActiveScoreCircle" \
           f"&param=%7B%22token%22%3A%22{token}%22%2C%22scoreCircleId%22%3A{active_dict['id']}%7D"
    headers = {
        'content-type': 'application/x-www-form-urlencoded'
    }
    try:
        res = requests.post("https://server.17wanxiao.com/YKT_Interface/score", data=data, headers=headers).json()
        msg = f'{active_dict["title"]}({active_dict["id"]})：{active_dict["foodCoupon"]}个粮票，'
        if res['result_']:
            log.info(msg + res['message_'])
        else:
            log.warning(msg + res['message_'])
    except Exception as e:
        log.warning(f'{e.__class__}:{e}操作失败')


def get_circle_score(token, circle_dict):
    """
    获取其他奖励
    """
    data = f"token={token}" \
           "&method=gainScoreCircle" \
           f"&param=%7B%22token%22%3A%22{token}%22%2C%22scoreCircleId%22%3A{circle_dict['id']}%7D"
    headers = {
        'content-type': 'application/x-www-form-urlencoded'
    }
    try:
        res = requests.post("https://server.17wanxiao.com/YKT_Interface/score", data=data, headers=headers).json()
        msg = f'{circle_dict["title"]}({circle_dict["id"]})：{circle_dict["foodCoupon"]}个粮票，'
        if res['result_']:
            log.info(msg + res['message_'])
        else:
            log.warning(msg + res['message_'])
    except Exception as e:
        log.warning(f'{e.__class__}:{e}操作失败')


def get_all_score(token):
    for _ in range(2):
        circle_dict_list = get_score_list(token)['circle']
        if circle_dict_list:
            for circle_dict in circle_dict_list:
                get_circle_score(token, circle_dict)
        else:
            break
