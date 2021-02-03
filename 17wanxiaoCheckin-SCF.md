# 🌈17wanxiaoCheckin-SCF

## 前言

由于 GitHub Actions 暂无法与完美校园交换密钥，可能完美校园把 GitHub Actions 的 IP 给 ban 了（猜测），暂时给出一个腾讯云函数版的解决方案，其余方案还有：服务器、[coding](https://blog.imyan.ren/posts/eb6032e9/)、手机（Tasker），以及其他可自动化运行python脚本的办法皆可！

## 前提

1. 已有腾讯云账号（没有，可以注册）
2. 腾讯云已实名（觉得实名有困难，不建议用）

## 使用方法

### 1、进入控制台

![进入控制台.png](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/进入控制台.png)

### 2、进入云函数

![进入云函数.png](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/搜索云函数.png)

### 3、新建云函数

![新建云函数.png](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/选择地区.png)

### 4、上传代码

在此下载 ，https://lingsiki.lanzous.com/b0ekc7p9i 密码：7dwe

同时请下载，RegisterDeviceID.zip 下来，后续获取 ID 需要。如若软件打不开，可自行下载模拟器，短信登陆完美校园之后，在模拟器设置中复制 IMEI（即为 DEVICEID 字段）

![上传代码.png](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/新建函数.png)

### 5、触发器配置

配置时间可具体参考，它下面的 [链接](https://cloud.tencent.com/document/product/583/9708)

每日 6 点打卡：`0 0 6 * * * *`

每日 6、12、17点打卡：`0 0 6,12,17 * * * *`

![设置触发器.png](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/设置触发器.png)

### 6、添加环境变量

- 设置 900 秒（**重点**），因为 3 秒太短啦！
- 可选参数，刚接触的朋友我强烈建议使用 QQ 邮箱的推送方式，因为推送消息最全面！
- 如果无误再转 Qmsg 酱（可选），Server酱云函数好像被 ban 了
- USERNAME 字段（必填）：手机号1,手机号2,......（与下面密码对应），例如：`1737782***,13602***`
- PASSWORD 字段（必填）：密码1,密码2,......  （与上面账号对应），例如：`123456,456789`
- DEVICEID 字段（必填）：设备id1,设备id2....（与上面账号对应），例如：`1232,12312`，没有请下载 RegisterDeviceID 获取
- SCKEY 字段（可选）：用来开启 Server 酱推送服务，填写一个即可，没有请前往 [Server酱](https://sc.ftqq.com/3.version) 注册获取
- KEY 字段（可选）：用来开启 Qmsg 酱推送服务，填写一个即可，没有请前往 [Qmsg酱](https://qmsg.zendee.cn/index.html) 注册获取
- SEND_EMAIL 字段（可选）：用来开启 QQ邮箱推送服务，QQ邮箱地址
- SEND_PWD 字段（可选）：用来开启 QQ邮箱推送服务，QQ邮箱授权码，**不是 QQ 密码**
- RECEIVE_EMAIL 字段（可选）：用来开启 QQ邮箱推送服务，接收邮箱地址，理论上什么邮箱都可

![编辑环境变量.png](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/编辑环境变量.png)

![设置环境变量.png](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/设置环境变量.png)

### 7、部署测试

每一次修改代码之后，一定要点一下测试（自动部署），或者部署代码才能生效
**查看推送情况，确认是否成功**，（检查打卡 json 字段中的 areaStr 是否为自己所在地址，如果不在，请一定要修改代码，因为打卡的地址不对可不行；如果 json 字段中还有其他字段，如 deptid，stuNo 等等为 null 或者不对，请务必修改代码，如果 Message 有值为 None（QQ 邮箱推送打卡表格数据），请一定要修改代码，因为该值无法自动填写）如果你显示打卡成功或打卡频繁，且推送的 Message 中没有 None 值，即为成功，**至此每日六点多将会自行打卡**，**修改代码方法在原仓库 [wiki](https://github.com/ReaJason/17wanxiaoCheckin-Actions/wiki) 中**，有问题提 [issue](https://github.com/ReaJason/17wanxiaoCheckin-Actions/issues)。

![测试.png](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/测试.png)

### 8、如果有什么报错或者其他问题，请前往 [这里](https://github.com/ReaJason/17wanxiaoCheckin-Actions/wiki) 自行解决

### 9、如果这篇教程有帮到你，或者仓库代码有帮到你，可以赞赏一杯奶茶，谢谢你的光顾！

<img src="https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/支付宝.jpg" width="300"/><img src="https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/微信.png" width="300"/>