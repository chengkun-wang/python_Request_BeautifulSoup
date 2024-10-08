import requests
import re
import pymysql
import json
import time


def get_json_page_a(page):
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


def get_json_page(url):
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


def format_time(content):
    strings = content.split('+0800', 2)[0] + content.split('+0800', 2)[1]
    mktime = time.mktime(time.strptime(strings, "%a %b %d %H:%M:%S %Y"))
    localtime = time.localtime(mktime)
    format_time = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
    return format_time


def format_sex(sex):
    if sex == 'f':
        return "女"
    else:
        return "男"


def get_selectd_messages(url):
    """
获取每个微博正文的url后，提取其中的评论
    :param url: json格式评论的url
    :return: 返回对应微博的评论信息
    """
    global dict
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            jsons = response.json()
            comment_number = len(jsons['data']['data'])
            comments_dict = {}
            for j in range(comment_number):
                text = jsons['data']['data'][j]['text']
                content = ''.join(re.findall('[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b'
                                             '\u4e00-\u9fa5]', text))
                time = jsons['data']['data'][j]['created_at']
                created_at = format_time(time)
                # print(created_at)
                user_id = jsons['data']['data'][j]['user']['id']
                user_name = jsons['data']['data'][j]['user']['screen_name']
                user_head_portrait = jsons['data']['data'][j]['user']['profile_image_url']
                gender = jsons['data']['data'][j]['user']['gender']
                user_gender = format_sex(gender)
                a = jsons['data']['data'][j]['comments']
                # print(type(a))
                if type(a) == bool:
                    dict = {
                        "评论内容": content,
                        "评论时间": created_at,
                        "评论用户ID": user_id,
                        "用户昵称": user_name,
                        "用户头像": user_head_portrait,
                        "用户性别": user_gender,
                        "回复": "该评论没有回复"
                    }
                    # print(dict)
                else:
                    counts = len(a)
                    if counts == 1:
                        text = a[0]['text']
                        reply_content = ''.join(re.findall('[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001'
                                                           '\uff1f\u300a\u300b\u4e00-\u9fa5]', text))
                        time = a[0]['created_at']
                        reply_created_at = format_time(time)
                        reply_user_id = a[0]['user']['id']
                        reply_user_name = a[0]['user']['screen_name']
                        reply_user_head_portrait = a[0]['user']['profile_image_url']
                        gender = a[0]['user']['gender']
                        reply_user_gender = format_sex(gender)
                        dict1 = {
                            "回复内容": reply_content,
                            "回复时间": reply_created_at,
                            "回复用户ID": reply_user_id,
                            "回复用户昵称": reply_user_name,
                            "回复用户头像": reply_user_head_portrait,
                            "回复用户性别": reply_user_gender
                        }
                        dict = {
                            "评论内容": content,
                            "评论时间": created_at,
                            "评论用户ID": user_id,
                            "用户昵称": user_name,
                            "用户头像": user_head_portrait,
                            "用户性别": user_gender,
                            "回复": dict1
                        }
                        # print(dict)
                    elif counts == 2:
                        text1 = a[0]['text']
                        reply_content1 = ''.join(re.findall('[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001'
                                                            '\uff1f\u300a\u300b\u4e00-\u9fa5]', text1))
                        time1 = a[0]['created_at']
                        reply_created_at1 = format_time(time1)
                        reply_user_id1 = a[0]['user']['id']
                        reply_user_name1 = a[0]['user']['screen_name']
                        reply_user_head_portrait1 = a[0]['user']['profile_image_url']
                        gender1 = a[0]['user']['gender']
                        reply_user_gender1 = format_sex(gender1)
                        dict1 = {
                            "回复内容": reply_content1,
                            "回复时间": reply_created_at1,
                            "回复用户ID": reply_user_id1,
                            "回复用户昵称": reply_user_name1,
                            "回复用户头像": reply_user_head_portrait1,
                            "回复用户性别": reply_user_gender1
                        }
                        text2 = a[1]['text']
                        reply_content2 = ''.join(re.findall('[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001'
                                                            '\uff1f\u300a\u300b\u4e00-\u9fa5]', text2))
                        time2 = a[1]['created_at']
                        reply_created_at2 = format_time(time2)
                        reply_user_id2 = a[1]['user']['id']
                        reply_user_name2 = a[1]['user']['screen_name']
                        reply_user_head_portrait2 = a[1]['user']['profile_image_url']
                        gender2 = a[1]['user']['gender']
                        reply_user_gender2 = format_sex(gender2)
                        dict2 = {
                            "回复内容": reply_content2,
                            "回复时间": reply_created_at2,
                            "回复用户ID": reply_user_id2,
                            "回复用户昵称": reply_user_name2,
                            "回复用户头像": reply_user_head_portrait2,
                            "回复用户性别": reply_user_gender2
                        }
                        dict = {
                            "评论内容": content,
                            "评论时间": created_at,
                            "评论用户ID": user_id,
                            "用户昵称": user_name,
                            "用户头像": user_head_portrait,
                            "用户性别": user_gender,
                            "回复1": dict1,
                            "回复2": dict2
                        }
                        # print(dict)
                comments_dict[str(j)] = dict
            return comments_dict
    except:
        return "暂无评论"


def get_vote_url(page, number):
    """
获取这条微博里的投票活动
    :param page: 这条微博所在的页码
    :param number: 这条微博所在页的第几条
    :return: 返回这条微博里投票活动的url
    """
    try:
        json = get_json_page_a(page)
        url = json['data']['cards'][number]['mblog']['page_info']['page_url']
        return url
    except:
        return " "


def get_video_url(page, number):
    """
获取这条微博内容里的视频
    :param page: 这条微博所在的页码
    :param number: 这条微博所在页的第几条
    :return: 返回这条微博里视频的url
    """
    try:
        json = get_json_page_a(page)
        url = json['data']['cards'][number]['mblog']['page_info']['media_info']['stream_url']
        return url
    except:
        return " "


def get_pics_url(search_url):
    try:
        dict = {}
        json = get_json_page(search_url)
        counts = len(json['data']['pics'])
        for count in range(counts):
            dict[str(count)] = json['data']['pics'][count]['url']
        return dict
    except:
        return " "


def save_to_db(**kwargs):
    try:
        db = pymysql.connect(host='localhost', user='root', password='103035', port=3306, db='sqltest', charset='utf8')
        cursor = db.cursor()
        sql = "insert IGNORE into djangoapp_microblog(发布时间, 微博内容, 评论, 投票活动, 视频, 图片, 点赞数, 评论数, 转发数)" \
              "values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        params = (
            kwargs["发布时间"], kwargs["微博内容"], kwargs["评论"], kwargs["投票活动"], kwargs["视频"],
            kwargs["图片"], kwargs["点赞数"], kwargs["评论数"], kwargs["转发数"])

        cursor.execute(sql, params)

        db.commit()
        cursor.close()
        db.close()
    except:
        print("连接失败")


if __name__ == '__main__':
    pages = range(1, 3)
    for page in pages:
        url = "https://m.weibo.cn/api/container/getIndex?uid=2376916624&" \
              "luicode=10000011&lfid=1076032376916624&type=uid&value=2376916624&" \
              "containerid=1076032376916624&page=" + str(page)
        page_content = get_json_page(url)
        numbers = len(page_content['data']['cards'])
        print(numbers)
        for number in range(1, numbers):
            Micro_blog_content = "".join(
                re.findall('[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\u4e00-\u9fa5]',
                           page_content['data']['cards'][number]['mblog']['text']))
            comments_url = 'https://m.weibo.cn/comments/hotflow?id=' + page_content['data']['cards'][number]['mblog']['id'] + \
                  '&mid=' + page_content['data']['cards'][number]['mblog']['id'] + '&max_id_type=0'
            comments = str(get_selectd_messages(comments_url))
            url_two = page_content['data']['cards'][number]['scheme']
            OBJ = re.findall('^.*?status/(.*?)\?mblogid.*?', url_two)
            id = "".join(OBJ)
            search_url = "https://m.weibo.cn/statuses/show?id=" + str(id)
            pics = str(get_pics_url(search_url))
            reply = get_json_page(search_url)
            created_at_time = reply['data']['created_at']
            created_at = format_time(created_at_time)
            praise_points = page_content['data']['cards'][number]['mblog']['attitudes_count']
            comment_numbers = page_content['data']['cards'][number]['mblog']['comments_count']
            forwarding_numbers = page_content['data']['cards'][number]['mblog']['reposts_count']
            vote = get_vote_url(page, number)
            video = get_video_url(page, number)
            data_dict = {
                "发布时间": created_at,
                "微博内容": Micro_blog_content,
                "图片": pics,
                "视频": video,
                "投票活动": vote,
                "点赞数": praise_points,
                "评论数": comment_numbers,
                "转发数": forwarding_numbers,
                "评论": comments
            }
            # save_to_db(**data_dict)
            print(data_dict)


# 遇到的一些问题
# 1."Data too long for column '发布时间' at row 1")
# mysql> SET @@global.sql_mode='';之后不再报错，而是警告。
# from requests.packages import urllib3
# urllib3.disable_warnings()用来关闭警告
# 2.由于微博中可能不会同时存在视频，投票活动，图片，通过json得到None。
# Warning: (1048, "Column '投票活动' cannot be null")
# 3.xadmin中删除一个自增id后位置空缺；
# mysql> alter table djangoapp_microblog AUTO_INCREMENT=1;进行重置id。
