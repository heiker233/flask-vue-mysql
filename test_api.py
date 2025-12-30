import requests

login_url = 'http://10.13.73.211:5000/api/login'
payload = {'username': 'admin', 'password': 'admin'}

response = requests.post(login_url, json=payload)

print('Status Code:', response.status_code)
print('Response Text:', response.text)
print('Response JSON:', response.json() if response.status_code == 200 else 'N/A')