import requests

base_url = "https://reportedh5.17wanxiao.com/sass/api/epmpics"


json = {"businessType": "epmpics", "method": "submitUpInfo",
        "jsonData": {"deptStr": {"deptid": 141659, "text": "土木工程学院-测绘工程-2017测绘工程2班"},
                     "areaStr": "{\"province\":\"湖南省\",\"city\":\"湘潭市\",\"district\":\"湘潭县\",\"streetNumber\":\"\","
                                "\"street\":\"\",\"pois\":\"义山公\",\"lng\":\"112.712495\",\"lat\":\"27.812259\","
                                "\"address\":\"湘潭县义山公\",\"text\":\"湖南省-湘潭市\",\"code\":\"\"}",
                     "reportdate": 1590483588292, "customerid": "1999", "deptid": 141659, "source": "alipay",
                     "templateid": "pneumonia", "stuNo": "20172987", "username": "冯剑平", "phonenum": "17377820279",
                     "userid": "13673775", "updatainfo": [{"propertyname": "bodyzk", "value": "正常温度(小于37.3)"},
                                                          {"propertyname": "istouchcb", "value": "自己家中"},
                                                          {"propertyname": "sfwz2", "value": "内地学生"},
                                                          {"propertyname": "symptom", "value": "无"},
                                                          {"propertyname": "homehealth", "value": "无"},
                                                          {"propertyname": "isConfirmed", "value": "无"},
                                                          {"propertyname": "ownbodyzk", "value": "良好"},
                                                          {"propertyname": "ishborwh", "value": "无"},
                                                          {"propertyname": "outdoor", "value": "绿色"},
                                                          {"propertyname": "isContactFriendIn14", "value": "没有"},
                                                          {"propertyname": "ownPhone", "value": "17377820279"},
                                                          {"propertyname": "emergencyContact", "value": "郑怀玲"},
                                                          {"propertyname": "mergencyPeoplePhone",
                                                           "value": "18674490817"}], "gpsType": 1}}

response = requests.post(base_url, json=json)
res = response.text
print(res)

