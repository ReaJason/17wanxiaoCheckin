"""
Server酱推送服务
https://sct.ftqq.com/
"""
import requests


def server_push(send_key, title, desp):
    """
    :param send_key: 官网获取 send_key，用来发送消息
    :param title: 发送消息的标题
    :param desp: 发送文本
    :return:
    """
    send_url = f"https://sctapi.ftqq.com/{send_key}.send"
    params = {"text": title, "desp": desp}
    try:
        res = requests.post(send_url, data=params).json()
        """
        {'message': '[AUTH]用户不存在或者权限不足', 'code': 40001, 'info': '用户不存在或者权限不足', 'args': [None]}
        {'code': 0, 'message': '', 'data': {'pushid': '851777', 'readkey': 'SCTHPzE9Yvar1eA', 'error': 'SUCCESS', 'errno': 0}}
        """
        if not res["code"]:
            return {"status": 1, "msg": "Server酱推送服务成功"}
        else:
            return {"status": 0, "errmsg": f"Server酱推送服务失败，{res['message']}"}
    except Exception as e:
        return {"status": 0, "errmsg": f"Server酱推送服务失败，{e}"}
