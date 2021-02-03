"""
QQ邮箱推送
小号往大号邮箱进行发送邮箱
"""

import smtplib
from email.mime.text import MIMEText
# from email.header import Header


def qq_email_push(send_email, send_pwd, receive_email, title, text, text_type="html"):
    """
    :param send_email: 发送邮箱的邮箱地址
                       默认为：qq邮箱，其他邮箱请修改stmp地址和端口
    :param send_pwd: 发送邮箱的邮箱授权码
    :param receive_email: 接收信息的邮箱地址（随意是什么邮箱）
                          如果是多个请列表传入 ["第一个", "第二个"]
    :param title: 邮箱标题
    :param text: 需要发送的消息
    :param text_type: 纯文本："plain"，默认为发送 html："html"
    :return:
    """
    stmp_address = "smtp.qq.com"   # stmp 服务地址
    stmp_port = 465                # stmp 服务端口
    msg = MIMEText(text, text_type, "utf-8")
    # msg["From"] = Header("Robot", "utf-8")  # 设置发送方别名
    msg["From"] = send_email
    msg["Subject"] = title
    try:
        with smtplib.SMTP_SSL(stmp_address, stmp_port) as server:
            server.login(send_email, send_pwd)
            server.sendmail(send_email, receive_email, msg.as_string())
            return {"status": 1, "msg": "QQ邮箱推送成功"}
    except Exception as e:
        return {"status": 0, "errmsg": f'QQ邮箱推送失败：{e}'}