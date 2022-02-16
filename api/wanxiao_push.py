import datetime
import json

from utils.bark import bark_push
from utils.server_chan import server_push
from utils.wechat_enterprise import wechat_enterprise_push
from utils.email_push import email_push
from utils.qmsg import qmsg_push
from utils.pipehub import pipe_push


def wanxiao_server_push(send_key, check_info_list):
    utc8_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    push_list = [f"""
------
#### 现在时间：
```
{utc8_time.strftime("%Y-%m-%d %H:%M:%S %p")}
```"""]
    for check_info in check_info_list:
        if check_info["status"]:
            if check_info["post_dict"].get("checkbox"):
                post_msg = "\n".join(
                    [
                        f"| {i['description']} | {i['value']} |"
                        for i in check_info["post_dict"]["checkbox"]
                    ]
                )
            else:
                post_msg = "暂无详情"
            name = check_info["post_dict"].get("username")
            if not name:
                name = check_info["post_dict"]["name"]
            push_list.append(
                f"""#### {name}{check_info['type']}打卡信息：
```
{json.dumps(check_info['check_json'], sort_keys=True, indent=4, ensure_ascii=False)}
```
------
| Text                           | Message |
| :----------------------------------- | :--- |
{post_msg}
------
```
{check_info['res']}
```"""
            )
        else:
            push_list.append(
                f"""------
#### {check_info['errmsg']}
------
"""
            )
    push_list.append(
        f"""
>
> [17wanxiaoCheckin](https://github.com/ReaJason/17wanxiaoCheckin-Actions)
>
>期待你给项目的star✨
"""
    )
    return server_push(send_key, "健康打卡", "\n".join(push_list))


def wanxiao_email_push(send_email, send_pwd, receive_email, smtp_address, smtp_port, check_info_list):
    mail_msg_list = []
    for check in check_info_list:
        if check["status"]:
            name = check['post_dict'].get('username')
            if not name:
                name = check['post_dict']['name']
            mail_msg_list.append(f"""<hr>
<details>
<summary style="font-family: 'Microsoft YaHei UI',serif; color: deepskyblue;">{name}：{check["type"]} 打卡结果：{check['res']}</summary>
<pre><code>
{json.dumps(check['check_json'], sort_keys=True, indent=4, ensure_ascii=False)}
</code></pre>
</details>
<details>
<summary style="font-family: 'Microsoft YaHei UI',serif; color: black;" >>>>填写数据抓包详情（用于 updatainfo 数据的修改）<<<</summary>
<pre><code>
{json.dumps(check['post_dict']['updatainfo_detail'], sort_keys=True, indent=4, ensure_ascii=False)}
</code></pre>
</details>
<span style="font-family: 'Microsoft YaHei UI',serif; color: lightskyblue;" >>>>打卡信息数据表格<<<</span>
<table id="customers">
<tr>
<th>Text</th>
<th>Value</th>
</tr>
"""
                                 )
            for index, box in enumerate(check["post_dict"]["checkbox"]):
                if index % 2:
                    mail_msg_list.append(
                        f"""<tr>
<td>{box['description']}</td>
<td>{box['value']}</td>
</tr>"""
                    )
                else:
                    mail_msg_list.append(f"""<tr class="alt">
<td>{box['description']}</td>
<td>{box['value']}</td>
</tr>"""
                                         )
            mail_msg_list.append(
                f"""
</table>"""
            )
        else:
            mail_msg_list.append(
                f"""<hr>
    <b style="color: red">{check['errmsg']}</b>"""
            )
    css = """<style type="text/css">
#customers
  {
  font-family:"Trebuchet MS", Arial, Helvetica, sans-serif;
  width:100%;
  border-collapse:collapse;
  }

#customers td, #customers th
  {
  font-size:1em;
  border:1px solid #98bf21;
  padding:3px 7px 2px 7px;
  }

#customers th
  {
  font-size:1.1em;
  text-align:left;
  padding-top:5px;
  padding-bottom:4px;
  background-color:#A7C942;
  color:#ffffff;
  }

#customers tr.alt td
  {
  color:#000000;
  background-color:#EAF2D3;
  }
</style>"""
    mail_msg_list.append(css)
    mail_msg_list.append(f"""
<h4><center> >>>>  <a href="https://github.com/ReaJason/17wanxiaoCheckin-Actions">17wanxiaoCheckin-Actions</a>
<<<<</center></h4>
""")
    return email_push(send_email, send_pwd, receive_email,
                      title="完美校园健康打卡", text="".join(mail_msg_list),
                      smtp_address=smtp_address, smtp_port=smtp_port)


def wanxiao_qmsg_push(key, qq_num, type, check_info_list):
    utc8_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    push_list = [f'@face=74@ {utc8_time.strftime("%Y-%m-%d %H:%M:%S")} @face=74@ ']
    for check_info in check_info_list:
        if check_info["status"]:
            name = check_info["post_dict"].get("username")
            if not name:
                name = check_info["post_dict"]["name"]
            push_list.append(f"""\
@face=54@ {name}{check_info['type']} @face=54@
@face=211@
{check_info['res']}
@face=211@""")
        else:
            push_list.append(check_info['errmsg'])
    return qmsg_push(key, qq_num, "\n".join(push_list), type)


def wanxiao_pipe_push(key, check_info_list):
    utc8_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    push_list = [f'打卡时间： {utc8_time.strftime("%Y-%m-%d %H:%M:%S")}']
    for check_info in check_info_list:
        if check_info["status"]:
            name = check_info["post_dict"].get("username")
            if not name:
                name = check_info["post_dict"]["name"]
            push_list.append(f"""\
{name}{check_info['type']}
{check_info['res']}
""")
        else:
            push_list.append(check_info['errmsg'])
    return pipe_push(key, "\n".join(push_list).encode())


def wanxiao_wechat_enterprise_push(corp_id, corp_secret, agent_id, to_user, check_info_list):
    utc8_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    push_list = [f'打卡时间：\n{utc8_time.strftime("%Y-%m-%d %H:%M:%S")}']
    for check_info in check_info_list:
        if check_info["status"]:
            name = check_info["post_dict"].get("username")
            if not name:
                name = check_info["post_dict"]["name"]
            push_list.append(f"{name}{check_info['type']}：\n{check_info['res']}")
        else:
            push_list.append(check_info['errmsg'])
    return wechat_enterprise_push(corp_id, corp_secret, agent_id, to_user, "\n".join(push_list))


def wanxiao_bark_push(device_key, group, check_info_list):
    utc8_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    title = f"""{utc8_time.strftime("%Y-%m-%d")}  健康打卡"""
    push_list = []
    for check_info in check_info_list:
        if check_info["status"]:
            name = check_info["post_dict"].get("username")
            if not name:
                name = check_info["post_dict"]["name"]
            if check_info['res']['code'] == "10000":
                push_list.append(f"""{name}：打卡{check_info['res']['msg']}😄😄😄""")
            else:
                push_list.append(f"""{name}：{check_info["res"]["data"]}😢😢😢""")
        else:
            push_list.append(check_info['errmsg'])
    return bark_push(device_key, "\n".join(push_list), title, group)
