import requests

# 测试前端代理
login_url = 'http://10.13.73.211:5173/api/login'
payload = {'username': 'admin', 'password': 'admin'}

response = requests.post(login_url, json=payload)

print('前端代理测试结果:')
print('Status Code:', response.status_code)
print('Response Text:', response.text)
print('Response JSON:', response.json() if response.status_code == 200 else 'N/A')
