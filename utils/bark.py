import json
import requests


def bark_push(device_key, msg, title, group):
    try:
        response = requests.post(
            url="https://api.day.app/push",
            headers={
                "Content-Type": "application/json; charset=utf-8",
            },
            data=json.dumps({
                "body": msg,
                "device_key": device_key,
                "title": title,
                "icon": "https://www.17wanxiao.com/new/images/logo.png",
                "group": group
            })
        ).json()
        if response['code']:
            return {"status": 1, "msg": "Bark推送成功"}
        return {"status": 0, "errmsg": f"Bark推送失败，{response['message']}"}
    except Exception as e:
        return {"status": 0, "errmsg": f"Bark推送失败，{e}"}
