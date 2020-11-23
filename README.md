# 🌈17wanxiaoCheckin-Actions



**💫2020.11.23：支持多人打卡，重写了一下代码**

**⚡2020.11.16：本项目已更新，使用本项目，你不需要抓包就可以使用（理论上大概......）**

[中南林业科技大学](https://www.csuft.edu.cn/) 测试可用，欢迎大家 fork 测试使用，如果可用的话，可以开 [issue](https://github.com/ReaJason/17wanxiaoCheckin-Actions/issues) 让更多人知道

感谢 [@zhongbr](https://github.com/zhongbr) 的完美校园逆向登录分析代码的分享：[完美校园模拟登录](https://github.com/zhongbr/wanmei_campus)

之前的抓包部署教程请前往：[完美校园抓包打卡](https://github.com/ReaJason/17wanxiaoCheckin-Actions/blob/master/README_LAST.md)



#### 一、功能介绍

1. 完美校园模拟登录获取token
2. 自动获取上次提交的打卡数据
3. 每天早上六点自动打卡（有 10+ 分钟延迟）
4. 微信推送打卡消息

#### 二、打卡数据

细心的你应该会发现，自从第一次打卡之后，每次进去信息基本自动填写好了，我抓取的就是这个接口，

这样子也相当于大家不用抓包了，如果你进入完美校园健康打卡界面，它没有自动填写信息，可能

本项目也就不起作用了，可以试试打一次卡然后再进入看有无自动填充信息。

```python
def get_post_json(self, token):
    jsons = {"businessType": "epmpics",
    "jsonData": {"templateid": "pneumonia", "token": token},
    "method": "userComeApp"}
    try:
        # 如果不请求一下这个地址，token就会失效
        requests.post("https://reportedh5.17wanxiao.com/api/clock/school/getUserInfo", data={'token': token})
        res = requests.post(url="https://reportedh5.17wanxiao.com/sass/api/epmpics", json=jsons).json()
    except:
        return None
    if res['code'] != '10000':
        return None
        data = json.loads(res['data'])
        post_dict = {
        "areaStr": data['areaStr'],
        "deptStr": data['deptStr'],
        "deptid": data['deptStr']['deptid'],
        "customerid": data['customerid'],
        "userid": data['userid'],
        "username": data['username'],
        "stuNo": data['stuNo'],
        "phonenum": data['phonenum'],
        "templateid": data['templateid'],
        "updatainfo": [{"propertyname": i["propertyname"], "value": i["value"]} for i in
        data['cusTemplateRelations']],
        "checkbox": [{"description": i["decription"], "value": i["value"]} for i in
        data['cusTemplateRelations']],
        }
        # print(json.dumps(post_dict, sort_keys=True, indent=4, ensure_ascii=False))
        # 在这里修改没有填写的数据，遍历post_dict['updatainfo']修改就行
        logging.info('获取完美校园打卡post参数成功')
        return post_dict
```



#### 三、使用方法

1. 请先确保进入健康打卡界面，信息能够正确的自动填写（没有自动填写的项，可以自行修改代码）

2. 点击右上角的 `fork`，`fork` 本项目到自己仓库中

   

   ![](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/click_fork.png)

   

3. 开启 `Actions`

   

   ![](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/start_action.png)

   

   ![](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/end_actions.png)

   

4. 设置三个 `secrets`  字段：`USERNAME`、`PASSWORD`、`SCKEY`（对应就是账号，密码以及 Server 酱）

   1. 如果是多人打卡的话：
      - USERNAME字段：手机号1,手机号2,......（与下面密码对应），例如：`1737782***,13602***`
      - PASSWORD字段：密码1,密码2,......  （与上面账号对应），例如：`123456,456789`
      - SCKEY字段：填写一个即可，例如：`SCU90543*******`

   

   ![](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/new_secrets.png)

   

   ![](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/secrets_details.png)

   

   ![](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/end_secrets.png)

   

5. 修改 `README.md` 测试一次

   

   ![](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/modify_readme.png)

   

   ![](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/end_modify.png)

   

6. 查看 `Actions` 运行情况，以及微信推送情况，至此每日六点多将会自行打卡

   

   ![](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/check_status.png)

   

   ![](https://cdn.jsdelivr.net/gh/ReaJason/17wanxiaoCheckin-Actions/Pictures/end_check.png)



