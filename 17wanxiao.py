import time
import json
import requests


base_url = "https://reportedh5.17wanxiao.com/sass/api/epmpics"

text = input()
address = input()
addtext = input()
deptId = eval(input())
userId = input()
stuNum = input()
userName = input()
phoneNum = input()
emergency = input()
emergencyPhone = input()


area = {'address': address, 'text': addtext, 'code': "430321"}

areaStr = json.dumps(area, ensure_ascii=False)

json = {"businessType": "epmpics", "method": "submitUpInfo",
        "jsonData": {"deptStr": {"deptid": deptId, "text": text},
                     "areaStr": areaStr,
                     "reportdate": round(time.time()*1000), "customerid": "1999", "deptid": deptId, "source": "alipay",
                     "templateid": "pneumonia", "stuNo": stuNum, "username": userName, "phonenum": phoneNum,
                     "userid": userId, "updatainfo": [{"propertyname": "bodyzk", "value": "正常温度(小于37.3)"},
                                                          {"propertyname": "istouchcb", "value": "自己家中"},
                                                          {"propertyname": "sfwz2", "value": "内地学生"},
                                                          {"propertyname": "symptom", "value": "无"},
                                                          {"propertyname": "homehealth", "value": "无"},
                                                          {"propertyname": "isConfirmed", "value": "无"},
                                                          {"propertyname": "ownbodyzk", "value": "良好"},
                                                          {"propertyname": "ishborwh", "value": "无"},
                                                          {"propertyname": "outdoor", "value": "绿色"},
                                                          {"propertyname": "isContactFriendIn14", "value": "没有"},
                                                          {"propertyname": "ownPhone", "value": phoneNum},
                                                          {"propertyname": "emergencyContact", "value": emergency},
                                                          {"propertyname": "mergencyPeoplePhone",
                                                           "value": emergencyPhone}], "gpsType": 0}}

response = requests.post(base_url, json=json)
print(response.text)

