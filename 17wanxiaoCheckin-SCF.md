# 🌈17wanxiaoCheckin-SCF

## 前言（GitHub Actions 已修复，可继续使用）

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

![上传代码.png](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/新建函数.png)

### 5、触发器配置

配置时间可具体参考，它下面的 [链接](https://cloud.tencent.com/document/product/583/9708)

每日 6 点打卡：`0 0 6 * * * *`

每日 6、12、17点打卡：`0 0 6,12,17 * * * *`

![设置触发器.png](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/设置触发器.png)

### 6、添加环境变量

- 设置900秒，不管为什么这么做，但是时长得拉满
- USERNAME字段：手机号1,手机号2,......（与下面密码对应），例如：`1737782***,13602***`
- PASSWORD字段：密码1,密码2,......  （与上面账号对应），例如：`123456,456789`
- SCKEY字段：填写一个即可，例如：`SCU90543*******`，没有请前往 [Server酱](https://sc.ftqq.com/3.version) 注册获取

![编辑环境变量.png](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/编辑环境变量.png)

![设置环境变量.png](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/设置环境变量.png)

### 7、部署测试

如果之前使用过GitHub Actions，请将代码该修改的地方修改，切勿全部复制粘贴，因为时间判定修改了

每一次修改代码之后，一定要点一下测试（自动部署），或者部署代码才能生效

查看微信推送情况（检查json 字段中的 areaStr 是否为自己所在地址，如果不在，请一定要修改代码，因为打卡的地址不对可不行；如果 Message 有值为 None，请一定要修改代码，因为该值无法自动填写），**至此每日六点多将会自行打卡**

![测试.png](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/测试.png)

### 8、如果有什么报错或者其他问题，请前往 [这里](https://github.com/ReaJason/17wanxiaoCheckin-Actions/wiki) 自行解决，或进群反馈没有解决的问题