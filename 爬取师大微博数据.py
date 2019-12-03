import requests
import re
import pymysql

def get_json_page(page):
    """获取json格式
    :param page: 要获取的页码
    :return: 返回json
    """
    url = "https://m.weibo.cn/api/container/getIndex?uid=2376916624&" \
          "luicode=10000011&lfid=1076032376916624&type=uid&value=2376916624&" \
          "containerid=1076032376916624&page=" + str(page)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        print("请求失败")


def get_selectd_messages(url):
    """
获取每个微博正文的url后，提取其中的评论
    :param url: json格式评论的url
    :return: 返回对应微博的评论信息
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            json = response.json()
            comment_number = len(json['data']['data'])
            comment_list = []
            for j in range(comment_number):
                content = json['data']['data'][j]['text']
                comment_list.append(content)
            return "".join(comment_list)
    except:
        return None


def get_pics(page, number):
    """
获取这条微博里的图片
    :param page: 这条微博所在的页码
    :param number: 这条微博所在页的第几条
    :return: 返回这条微博里图片的url
    """
    try:
        json = get_json_page(page)
        url_list = []
        counts = len(json['data']['cards'][number]['mblog']['pics'])
        for count in range(counts):
            url = json['data']['cards'][number]['mblog']['pics'][count]['url']
            url_list.append(url)
            url_list.append(',')
        return "".join(url_list)
    except:
        return None
    # return " "


def get_vote_url(page, number):
    """
获取这条微博里的投票活动
    :param page: 这条微博所在的页码
    :param number: 这条微博所在页的第几条
    :return: 返回这条微博里投票活动的url
    """
    try:
        json = get_json_page(page)
        url = json['data']['cards'][number]['mblog']['page_info']['page_url']
        return url
    except:
        return None
    # return " "


def get_video_url(page, number):
    """
获取这条微博内容里的视频
    :param page: 这条微博所在的页码
    :param number: 这条微博所在页的第几条
    :return: 返回这条微博里视频的url
    """
    try:
        json = get_json_page(page)
        url = json['data']['cards'][number]['mblog']['page_info']['media_info']['stream_url']
        return url
    except:
        return None
#     return " "



def save_to_db(**kwargs):
    try:
        db = pymysql.connect(host='localhost', user='root', password='103035', port=3306, db='sqltest', charset='utf8')
        cursor = db.cursor()
        sql = "insert IGNORE into djangoapp_microblog(发布时间, 微博内容, 评论, 投票活动, 视频, 图片, 点赞数, 评论数, 转发数)values " \
              "(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        params = (
            kwargs["发布时间"], kwargs["微博内容"], kwargs["评论"], kwargs["投票"], kwargs["视频"], kwargs["图片"], kwargs["点赞数"],
            kwargs["评论数"],
            kwargs["转发数"])

        cursor.execute(sql, params)

        db.commit()
        cursor.close()
        db.close()
    except:
        pass


if __name__ == '__main__':
    # 写一个input，判断输入
    pages = range(1, 3)
    for page in pages:
        json = get_json_page(page)
        numbers = len(json['data']['cards'])
        for number in range(1, numbers):
            try:
                url = 'https://m.weibo.cn/api/comments/show?id=' + json['data']['cards'][number]['mblog']['id']
                selectd_messages = get_selectd_messages(url)
                release_time = json['data']['cards'][number]['mblog']['created_at']
                Micro_blog_content = "".join(
                    re.findall('[\u4e00-\u9fa5]', json['data']['cards'][number]['mblog']['text']))
                praise_points = json['data']['cards'][number]['mblog']['attitudes_count']
                comment_numbers = json['data']['cards'][number]['mblog']['comments_count']
                forwarding_numbers = json['data']['cards'][number]['mblog']['reposts_count']
                vote = get_vote_url(page, number)
                video = get_video_url(page, number)
                pics = get_pics(page, number)

                dict = {
                    "发布时间": release_time,
                    "微博内容": Micro_blog_content,
                    "评论": selectd_messages,
                    "点赞数": praise_points,
                    "评论数": comment_numbers,
                    "转发数": forwarding_numbers,
                    "图片": pics,
                    "视频": video,
                    "投票": vote
                }
                save_to_db(**dict)
            except:
                print("此位置等待发表新的微博哦")


# 遇到的一些问题
# 1."Data too long for column '发布时间' at row 1")
# mysql> SET @@global.sql_mode='';之后不再报错，而是警告。
# from requests.packages import urllib3
# urllib3.disable_warnings()用来关闭警告
#2.由于微博中可能不会同时存在视频，投票活动，图片，通过json得到None。
# Warning: (1048, "Column '投票活动' cannot be null")
# 3.xadmin中删除一个自增id后位置空缺；
#mysql> alter table djangoapp_microblog AUTO_INCREMENT=1;进行重置id。