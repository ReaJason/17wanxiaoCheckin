import time
import json
import requests


base_url = "https://reportedh5.17wanxiao.com/sass/api/epmpics"


streetNumber = ""
street = input()
district = input()
city = input()
province = input()
town = ""
pois = input()
lng = eval(input())
lat = eval(input())
address = district + street + pois
text = province + "-" + city
code = ""
deptId = eval(input())
deptText = input()
userId = input()
stuNum = input()
userName = input()
phoneNum = input()
emergency = input()
emergencyPhone = input()


area = {'streetNumber': streetNumber,
        'street': street,
        'district': district,
        'city': city,
        'province': province,
        'town': town,
        'pois': pois,
        'lng': lng,
        'lat': lat,
        'address': address,
        'text': text,
        'code': ""}

areaStr = json.dumps(area, ensure_ascii=False)

json = {"businessType": "epmpics", "method": "submitUpInfo",
        "jsonData": {"deptStr": {"deptid": deptId, "text": deptText},
                     "areaStr": areaStr,
                     "reportdate": round(time.time()*1000), "customerid": "1000178", "deptid": deptId, "source": "app",
                     "templateid": "pneumonia", "stuNo": stuNum, "username": userName, "phonenum": phoneNum,
                     "userid": userId,
                     "updatainfo": [{"propertyname": "temperature", "value": "36.3"},
                                      {"propertyname": "wengdu", "value": "0"},
                                      {"propertyname": "isConfirmed", "value": "否"},
                                      {"propertyname": "isdefinde", "value": "否.未隔离"},
                                      {"propertyname": "isGoWarningAdress", "value": "否"},
                                      {"propertyname": "isIsolation", "value": "否"},
                                      {"propertyname": "isTouch", "value": "否"},
                                      {"propertyname": "isTransitArea", "value": "否"},
                                      {"propertyname": "isTransitProvince", "value": "否"},
                                      {"propertyname": "isFFHasSymptom", "value": "没有"},
                                      {"propertyname": "isContactFriendIn14", "value": "没有"},
                                      {"propertyname": "xinqing", "value": "健康"},
                                      {"propertyname": "bodyzk", "value": "否"},
                                      {"propertyname": "cxjh", "value": "否"},
                                      {"propertyname": "isleaveaddress", "value": "否"},
                                      {"propertyname": "isAlreadyInSchool", "value": "没有"},
                                      {"propertyname": "assistRemark", "value": ""},
                                      {"propertyname": "ownPhone", "value": phoneNum},
                                      {"propertyname": "emergencyContact", "value": emergency},
                                      {"propertyname": "mergencyPeoplePhone", "value": emergencyPhone}],
                     "gpsType": 0
                     }
        }

response = requests.post(base_url, json=json)
print(response.text)

