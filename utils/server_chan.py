"""
Server酱推送服务
https://sc.ftqq.com/3.version
"""
import requests


def server_push(sckey, title, desp):
    """
    :param sckey: 官网获取 sckey，用来发送消息，测试版请修改接口 url 地址
    :param title: 发送消息的标题
    :param desp: 发送文本
    :return:
    """
    send_url = f"https://sc.ftqq.com/{sckey}.send"
    params = {"text": title, "desp": desp}
    try:
        res = requests.post(send_url, data=params).json()
        """
        {"errno":1024,"errmsg":"bad pushtoken"}
        {"errno":0,"errmsg":"success","dataset":"done"}
        {"errno":1024,"errmsg":"不要发送重复的内容"}
        """
        if not res["errno"]:
            return {"status": 1, "msg": "Server酱推送服务成功"}
        else:
            return {"status": 0, "errmsg": f"Server酱推送服务失败，{res['errmsg']}"}
    except Exception as e:
        return {"status": 0, "errmsg": f"Server酱推送服务失败，{e}"}
