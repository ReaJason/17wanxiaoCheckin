#!/bin/sh


# crontab 需要引入python的环境变量，如果crontab不执行，sh checkin.sh却可以执行，请按照以下步骤解决
# 通过whereis python3查看python3的实际安装位置 出现xxx/bin/python3就是
# 将以下两行增加到/etc/profile文件的末尾,其中python3的位置取决于你实际安装位置
# export PATH="$PATH:/usr/bin/python3"  
# export PATH="$PATH:/usr/bin/python3.8"

source /etc/profile
# source ~/.bashrc
# source ~/.zshrc

#替换成你服务器的实际路径
#/usr/bin/python3 /home/wanmeicheckin/17wanxiao.py <<EOF
python3 /home/wanmeicheckin/17wanxiao.py <<EOF
账号
密码
server酱的skey
EOF