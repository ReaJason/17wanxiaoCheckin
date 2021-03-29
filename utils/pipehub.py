"""
PipeHub
https://www.pipehub.net/
"""
import requests


def pipe_push(callbackCode, content):
    """
    :param callbackCode: 官网获取 Callback URL，最后一个/后的代码
    :param content: 发送文本
    :return:
    """
    send_url = f"https://www.pipehub.net/send/{callbackCode}"
    try:
        res = requests.post(send_url, data=content).json()
        """
        {'request_id': 'b5436e9d-af52-4044-aae8-90b49222efe0', 'success': True, 'error_message': '', 'hint': 'Retried 0 times.'}
        """
        if res["success"]:
            return {"status": 1, "msg": "PipeHub推送成功"}
        else:
            return {"status": 0, "errmsg": f"PipeHub推送失败，{res['error_message']}"}
    except Exception as e:
        return {"status": 0, "errmsg": f"PipeHub推送失败，{e}"}
