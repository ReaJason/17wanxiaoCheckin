"""
企业微信推送
https://work.weixin.qq.com/
"""
import json

import requests


def wechat_enterprise_push(corp_id, corp_secret, agent_id, to_user, msg):
    """
    
    :param corp_id: 企业 ID
    :param corp_secret: 自建应用 Secret
    :param agent_id: 应用 ID
    :param to_user: 接收者用户，多用户用|分割，所有用户填写 @all
    :param msg: 推送消息
    :return:
    """
    # 获取 access_token
    get_access_token_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
    values = {
        'corpid': corp_id,
        'corpsecret': corp_secret,
    }
    try:
        res = requests.post(get_access_token_url, params=values).json()
        if not res['errcode']:
            access_token = res["access_token"]
        elif res['errcode'] == 40001:
            return {"status": 0, "errmsg": "不合法的 secret 参数，https://open.work.weixin.qq.com/devtool/query?e=40001"}
        elif res['errcode'] == 40013:
            return {"status": 0, "errmsg": "不合法的 CorpID，https://open.work.weixin.qq.com/devtool/query?e=40013"}
        else:
            return {"status": 0, "errmsg": res['errmsg']}
    except Exception as e:
        return {"status": 0, "errmsg": f"获取企业微信 access_token 失败，{e}"}
    
    # 推送消息
    send_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'
    post_data = {
        "touser": to_user,
        "msgtype": "text",
        "agentid": agent_id,
        "text": {
            "content": msg
        },
        "safe": "0"
    }
    try:
        res = requests.post(send_url, data=json.dumps(post_data)).json()
        if not res['errcode']:
            return {"status": 1, "msg": "企业微信推送服务成功"}
        elif res['errcode'] == 40056:
            return {"status": 0, "errmsg": "不合法的 agentid，https://open.work.weixin.qq.com/devtool/query?e=40056"}
        elif res['reecode'] == 81013:
            return {"status": 0,
                    "errmsg": "UserID、部门 ID、标签 ID 全部非法或无权限，https://open.work.weixin.qq.com/devtool/query?e=81013"}
    except Exception as e:
        return {"status": 0, "errmsg": f"企业微信推送服务失败，{e}"}
