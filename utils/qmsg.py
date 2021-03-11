"""
Qmsg酱
https://qmsg.zendee.cn/index.html
"""
import requests


def qmsg_push(key, qq_num, msg, send_type="send"):
    """
    :param key: qmsg酱的key，官网获取
    :param qq_num: qq号或qq群组号，要与 send_type 对应
    :param msg: 发送消息
    :param send_type: 发送模式，"send"为发送给个人，"group"为发送给群组
    :return:
    """
    post_data = {
        "msg": msg,
        "qq": qq_num
    }
    try:
        res = requests.post(f"https://qmsg.zendee.cn/{send_type}/{key}", data=post_data).json()
        """
        {"success":true,"reason":"操作成功","code":0,"info":{}}
        {"success":false,"reason":"消息内容不能为空","code":500,"info":{}}
        """
        if res['success']:
            return {"status": 1, "msg": "Qmsg酱推送服务成功"}
        return {"status": 0, "errmsg": f"Qmsg酱推送服务失败，{res['reason']}"}
    except Exception as e:
        return {"status": 0, "errmsg": f"Qmsg酱推送服务失败，{e}"}

