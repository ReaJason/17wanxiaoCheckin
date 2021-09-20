from setting import log
from utils.server_chan import server_push
from utils.wechat_enterprise import wechat_enterprise_push
from utils.email_push import email_push
from utils.qmsg import qmsg_push
from utils.pipehub import pipe_push
from core.base_push import BasePush


def info_push(push_dict, raw_info):
    push_funcs = {
        "email": EmailPush,
        "wechat": ServerPush,
        "qmsg": QmsgPush,
        "pipehub": PipePush,
        "wechat_enterprise": WechatEnterprisePush,
    }
    push_raw_info = {"push_info": raw_info}

    for push_name, push_func in push_funcs.items():
        enable = push_dict.get(push_name).get("enable")
        if not enable:
            pass
        else:
            del push_dict[push_name]["enable"]
            push_dict[push_name].update(push_raw_info)
            params_dict = push_dict[push_name]
            push_res = push_func(**params_dict).push()
            if push_res["status"]:
                log.info("【推送成功】—— " + push_res["msg"])
            else:
                log.warning("【推送失败】—— 错误原因：" + push_res["errmsg"])


class ServerPush(BasePush):
    def __init__(self, push_info, send_key):
        super().__init__(push_info)
        self.send_key = send_key

    def push(self):
        date_format = """------
#### 现在时间：
```
{0}
```"""
        success_format = """#### {0}{1}打卡信息：
```
{2}
```
```
{3}
```
"""
        errmsg_format = """------
#### {0}
------
"""
        info = super(ServerPush, self).parse_push_info(
            date_format, "", errmsg_format, True, success_format, True
        )
        return server_push(self.send_key, "健康打卡", info)


class EmailPush(BasePush):
    def __init__(
        self, push_info, send_email, send_pwd, receive_email, smtp_address, smtp_port
    ):
        super().__init__(push_info)
        self.smtp_port = smtp_port
        self.smtp_address = smtp_address
        self.receive_email = receive_email
        self.send_pwd = send_pwd
        self.send_email = send_email

    def push(self):
        date_format = "<h3><center> {0} </center></h3>"
        success_format = """\<hr>
<details>
<summary style="font-family: 'Microsoft YaHei UI',serif; color: deepskyblue;">{0}：{1} 打卡结果：{2}</summary>
<pre><code>
{3}
</code></pre>
</details>
<details>
<summary style="font-family: 'Microsoft YaHei UI',serif; color: black;" >>>>填写数据抓包详情（用于 updatainfo 数据的修改）<<<</summary>
<pre><code>
{4}
</code></pre>
</details>"""
        errmsg_format = "<hr><b style='color: red'>{0}</b><br>"
        info = super(EmailPush, self).parse_push_info(
            date_format, "", errmsg_format, True, success_format, True
        )
        return email_push(
            self.send_email,
            self.send_pwd,
            self.receive_email,
            title="完美校园健康打卡",
            text=info,
            smtp_address=self.smtp_address,
            smtp_port=self.smtp_port,
        )


class QmsgPush(BasePush):
    def __init__(self, push_info, key, send_type, qq_num):
        super().__init__(push_info)
        self.send_type = send_type
        self.qq_num = qq_num
        self.key = key

    def push(self):
        date_format = "@face=74@ {0} @face=74@"
        success_format = """\
@face=54@ {0}{1} @face=54@
@face=211@
{2}
@face=211@"""
        errmsg_format = "{0}"
        info = super(QmsgPush, self).parse_push_info(
            date_format, success_format, errmsg_format
        )
        return qmsg_push(self.key, self.qq_num, info, self.send_type)


class PipePush(BasePush):
    def __init__(self, push_info, key):
        super().__init__(push_info)
        self.key = key

    def push(self):
        date_format = "打卡时间： {0}"
        success_format = """\
{0}{1}
{2}
"""
        errmsg_format = "{0}"
        info = super(PipePush, self).parse_push_info(
            date_format, success_format, errmsg_format
        )
        return pipe_push(self.key, info.encode())


class WechatEnterprisePush(BasePush):
    def __init__(self, push_info, corp_id, corp_secret, agent_id, to_user):
        super().__init__(push_info)
        self.agent_id = agent_id
        self.corp_secret = corp_secret
        self.corp_id = corp_id
        self.to_user = to_user

    def push(self):
        date_format = "打卡时间：\n{0}"
        success_format = "{0}{1}：\n{2}"
        errmsg_format = "{0}"
        info = super(WechatEnterprisePush, self).parse_push_info(
            date_format, success_format, errmsg_format
        )
        return wechat_enterprise_push(
            self.corp_id, self.corp_secret, self.agent_id, self.to_user, info
        )
