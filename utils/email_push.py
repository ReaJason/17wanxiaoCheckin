"""
QQ邮箱推送
小号往大号邮箱进行发送邮箱
"""

import smtplib
from email.mime.text import MIMEText
# from email.header import Header


def email_push(send_email, send_pwd, receive_email, title, text, 
               text_type="html", smtp_address="smtp.qq.com", smtp_port=465):
    """
    :param send_email: 发送邮箱的邮箱地址
                       默认为：qq 邮箱，其他邮箱请修改 stmp 地址和端口
    :param send_pwd: 发送邮箱的邮箱授权码
    :param receive_email: 接收信息的邮箱地址（随意是什么邮箱）
                          如果是多个请列表传入 ["第一个", "第二个"]
    :param title: 邮箱标题
    :param text: 需要发送的消息
    :param text_type: 纯文本："plain"，默认为发送 html："html"
    :param smtp_address: stmp 服务地址
    :param smtp_port: stmp 服务端口
    :return:
    """
    msg = MIMEText(text, text_type, "utf-8")
    # msg["From"] = Header("LingSiKi", "utf-8")  # 设置发送方别名
    msg["From"] = send_email
    msg["Subject"] = title
    try:
        with smtplib.SMTP_SSL(smtp_address, smtp_port) as server:
            server.login(send_email, send_pwd)
            server.sendmail(send_email, receive_email, msg.as_string())
            return {"status": 1, "msg": "邮箱推送成功"}
    except Exception as e:
        return {"status": 0, "errmsg": f'邮箱推送失败：{e}'}