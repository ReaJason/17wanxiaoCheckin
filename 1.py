import requests

url = "https://server.59wanmei.com/YKT_Interface/xyk"

payload = 'token=e54cf47e-e570-4a95-91f4-c953a863e017&method=WX_getScoreShopUrl&param=%7B%22token%22%3A%22e54cf47e-e570-4a95-91f4-c953a863e017%22%7D'
headers = {
  'referer': 'https://server.59wanmei.com/YKT_Interface/inspire/foodTicket.html?customerId=1999&systemType=Android&UAinfo=wanxiao&versioncode=10531101&token=e54cf47e-e570-4a95-91f4-c953a863e017',
  'x-requested-with': 'com.newcapec.mobile.ncp',
  'cookie': 'Hm_lvt_5f5c3eda1b60c399abc780fdcc2a7322=1605095658;_ga=GA1.2.227897213.1605095658;Hm_lpvt_5f5c3eda1b60c399abc780fdcc2a7322=1605097614;sid=OVhZNldZYjktOVhidC1ZQ1pYLVp2V1ktNlpYckN4R3I5dHZi',
  'Content-Type': 'application/x-www-form-urlencoded'
}

response = requests.request("POST", url, headers=headers, data = payload)

print(response.text.encode('utf8'))