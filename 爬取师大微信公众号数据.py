from selenium import webdriver
import time
import json
import random
import requests
import re
import pymysql

# from requests.packages import urllib3


# 登录微信公众号，获取登录之后的cookies信息，并保存到本地文本中
def Wechat_login():
    driver = webdriver.Firefox()
    driver.get('https://mp.weixin.qq.com/')
    driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[2]/div/div/form/div[1]/div[1]/div/span/input').clear()
    driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[2]/div/div/form/div[1]/div[1]/div/span/input'). \
        send_keys('1030354667@qq.com')
    time.sleep(2)
    driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[2]/div/div/form/div[1]/div[2]/div/span/input').clear()
    driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[2]/div/div/form/div[1]/div[2]/div/span/input'). \
        send_keys('wck123,,,')
    time.sleep(2)
    driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[2]/div/div/form/div[3]/label').click()
    time.sleep(2)
    driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[2]/div/div/form/div[4]/a').click()
    time.sleep(15)
    cookies = driver.get_cookies()

    cookie = {}
    for items in cookies:
        cookie[items.get('name')] = items.get('value')

    with open('cookies.txt', 'w') as file:
        file.write(json.dumps(cookie))

    driver.close()


# 爬取微信公众号文章，并存在本地文本中
def get_content(query):
    # query为要爬取的公众号名称
    # 公众号主页
    url = 'https://mp.weixin.qq.com'

    # 设置headers
    headers = {
        'UserAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0',
        'Referer': 'https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=10&'
                   'share=1&token=1430976050&lang=zh_CN',
        'Host': 'mp.weixin.qq.com'
    }

    # 读取上一步获取到的cookies
    with open('cookies.txt', 'r', encoding='utf-8') as f:
        cookie = f.read()
    cookies = json.loads(cookie)
    # 增加重试连接次数(跨请求保持某些参数，保持登入状态)
    session = requests.Session()
    session.keep_alive = False
    # 增加重试连接次数
    session.adapters.DEFAULT_RETRIES = 511
    time.sleep(5)

    # 登录之后的微信公众号首页url变化为：https://mp.weixin.qq.com/cgi-bin/home?t=home/index&lang=zh_CN&token=1849751598，从这里获取token信息
    response = session.get(url=url, cookies=cookies, verify=False)

    token = re.findall(r'token=(\d+)', str(response.url))[0]
    time.sleep(2)
    # 搜索微信公众号的接口地址
    search_url = 'https://mp.weixin.qq.com/cgi-bin/searchbiz?'
    # 搜索微信公众号接口需要传入的参数，有三个变量：微信公众号token、随机数random、搜索的微信公众号名字
    query_id = {
        'action': 'search_biz',
        'token': token,
        'lang': 'zh_CN',
        'f': 'json',
        'ajax': '1',
        'random': random.random(),
        'query': query,
        'begin': '0',
        'count': '5'
    }
    # 打开搜索微信公众号接口地址，需要传入相关参数信息如：cookies、params、headers
    search_response = session.get(
        search_url,
        cookies=cookies,
        headers=headers,
        params=query_id)
    # 取搜索结果中的第一个公众号
    lists = search_response.json().get('list')[0]
    print(lists)
    # 获取这个公众号的fakeid，后面爬取公众号文章需要此字段
    fakeid = lists.get('fakeid')

    # 微信公众号文章接口地址
    appmsg_url = 'https://mp.weixin.qq.com/cgi-bin/appmsg?'
    # 搜索文章需要传入几个参数：登录的公众号token、要爬取文章的公众号fakeid、随机数random
    query_id_data = {
        'token': token,
        'lang': 'zh_CN',
        'f': 'json',
        'ajax': '1',
        'random': random.random(),
        'action': 'list_ex',
        'begin': '0',  # 不同页，此参数变化，变化规则为每页加5
        'count': '5',
        'query': '',
        'fakeid': fakeid,
        'type': '9'
    }
    # 打开搜索的微信公众号文章列表页
    appmsg_response = session.get(
        appmsg_url,
        cookies=cookies,
        headers=headers,
        params=query_id_data)
    # 获取文章总数
    max_num = appmsg_response.json().get('app_msg_cnt')
    print("共有%d页" % int(int(max_num) / 5 + 1))
    start = int(input("请输入开始爬取的页码："))
    end = int(input("请输入结束爬取的页码："))
    while (end - start) + 1 > 0:
        query_id_data = {
            'token': token,
            'lang': 'zh_CN',
            'f': 'json',
            'ajax': '1',
            'random': random.random(),
            'action': 'list_ex',
            'begin': '{}'.format(str(start * 5 - 5)),
            'count': '5',
            'query': '',
            'fakeid': fakeid,
            'type': '9'
        }
        print('正在爬取第%d页' % start)
        query_fakeid_response = requests.get(
            appmsg_url,
            cookies=cookies,
            headers=headers,
            params=query_id_data)
        jsons = query_fakeid_response.json()
        length = len(jsons['app_msg_list'])
        for each in range(length):
            title = jsons['app_msg_list'][each]['title']
            digest = jsons['app_msg_list'][each]['digest']
            link = jsons['app_msg_list'][each]['link']
            dict = {
                '标题': title,
                '摘要': digest,
                'URL': link
            }
            save_to_db(**dict)
        start = start + 1
        print('正在翻页，请耐心等待')
        time.sleep(2)
    # print("共有%d页" % max_num+1)
    # start = int(input("请输入开始爬取的页码："))
    # end = int(input("请输入结束爬取的页码："))
    # while (end - start) + 1 > 0:
    #     query_id_data = {
    #         'token': token,
    #         'lang': 'zh_CN',
    #         'f': 'json',
    #         'ajax': '1',
    #         'random': random.random(),
    #         'action': 'list_ex',
    #         'begin': '{}'.format(str(start*5-5)),
    #         'count': '5',
    #         'query': '',
    #         'fakeid': fakeid,
    #         'type': '9'
    #     }
    #     print('正在爬取第%d页' % start)
    #     query_fakeid_response = requests.get(
    #         appmsg_url,
    #         cookies=cookies,
    #         headers=headers,
    #         params=query_id_data)
    #     json = query_fakeid_response.json()
    #     length = len(json['app_msg_list'])
    #     for each in range(length):
    #         title = json['app_msg_list'][each]['title']
    #         digest = json['app_msg_list'][each]['digest']
    #         link = json['app_msg_list'][each]['link']
    #         dict = {
    #             '标题': title,
    #             '摘要': digest,
    #             'URL': link
    #         }



    # 每页至少有5条，获取文章总的页数，爬取时需要分页爬
    # num = int(int(max_num) / 5)
    # # 起始页begin参数，往后每页加5
    # begin = 0
    # seq = 0
    # while num + 1 > 0:
    #     query_id_data = {
    #         'token': token,
    #         'lang': 'zh_CN',
    #         'f': 'json',
    #         'ajax': '1',
    #         'random': random.random(),
    #         'action': 'list_ex',
    #         'begin': '{}'.format(str(begin)),
    #         'count': '5',
    #         'query': '',
    #         'fakeid': fakeid,
    #         'type': '9'
    #     }
    #     print('正在翻页：--------------', begin)
        # time.sleep(5)

        # # 获取每一页文章的标题和链接地址，并写入本地文本中
        # query_fakeid_response = requests.get(
        #     appmsg_url,
        #     cookies=cookies,
        #     headers=headers,
        #     params=query_id_data)
        # fakeid_list = query_fakeid_response.json().get('app_msg_list')
        # if fakeid_list:
        #     for item in fakeid_list:
        #         content_link = item.get('link')
        #         content_title = item.get('title')
        #         fileName = query + '.txt'
        #         seq += 1
        #         with open(fileName, 'w', encoding='utf-8') as fh:
        #             fh.write(
        #                 str(seq) +
        #                 "|" +
        #                 content_title +
        #                 "|" +
        #                 content_link +
        #                 "\n")
        # num -= 1
        # begin = int(begin)
        # begin += 5


def save_to_db(**kwargs):
    try:
        db = pymysql.connect(host='localhost', user='root', password='103035', port=3306, db='sqltest', charset='utf8')
        cursor = db.cursor()
        sql = "insert IGNORE into djangoapp_wechat(标题, 摘要, URL)values (%s, %s, %s)"
        params = (
            kwargs["标题"], kwargs["摘要"], kwargs["URL"])

        cursor.execute(sql, params)

        db.commit()
        cursor.close()
        db.close()
    except:
        pass


if __name__ == '__main__':
    # 登录微信公众号，获取登录之后的cookies信息，并保存到本地文本中
    Wechat_login()
    query = "江西师范大学"
    print("开始爬取公众号：" + query)
    get_content(query)
    print("爬取完成")
    # #登录之后，通过微信公众号后台提供的微信公众号文章接口爬取文章
    # for query in gzlist:
    #     #爬取微信公众号文章，并存在本地文本中
    #     print("开始爬取公众号："+query)
    #     get_content(query)
    #     print("爬取完成")