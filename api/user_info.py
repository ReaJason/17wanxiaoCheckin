import requests


def get_school_name(token):
    post_data = {"token": token, "method": "WX_BASE_INFO", "param": "%7B%7D"}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    try:
        res = requests.post(
            "https://server.59wanmei.com/YKT_Interface/xyk",
            data=post_data,
            headers=headers,
            timeout=10
        )
        return res.json()["data"]["customerName"]
    except:
        return "Bad Req"


def get_user_info(token):
    data = {"appClassify": "DK", "token": token}
    for _ in range(3):
        try:
            res = requests.post(
                "https://reportedh5.17wanxiao.com/api/clock/school/getUserInfo", data=data, timeout=10
            )
            user_info = res.json()["userInfo"]
            user_info['school'] = get_school_name(token)
            return user_info
        except TimeoutError:
            continue
        except:
            return None
    return None
