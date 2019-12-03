import requests
import json
import random
import re
with open('cookies.txt', 'r') as file:
    cookie = file.read()
uniform = random.uniform(0, 1)
random = round(uniform, 16)
begin = 0

url = "https://mp.weixin.qq.com"

headers = {
    'UserAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0',
    'Referer': 'https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&' \
              'action=edit&isNew=1&type=10&share=1&token=1430976050&lang=zh_CN',
    'Host': 'mp.weixin.qq.com'
}

cookies = json.loads(cookie)

response = requests.get(url, cookies=cookies)
token = re.findall(r'token=(\d+)', str(response.url))[0]
print(token)


data = {
    'token': token,
    'lang': 'zh_CN',
    'f': 'json',
    'ajax': '1',
    'random': random,
    'action': 'list_ex',
    'begin': begin,
    'count': '10',
}

search_url = 'https://mp.weixin.qq.com/cgi-bin/operate_appmsg?sub=can_reprint_article_list'

search_response = requests.post(search_url, cookies=cookies, data=data, headers=headers)
print(search_response.text)