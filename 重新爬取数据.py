import pymysql

def fun(name):
    try:
        db = pymysql.connect(host='localhost', user='root', password='103035', port=3306, db='sqltest', charset='utf8')
        cursor = db.cursor()
        sql = "alter table %s AUTO_INCREMENT=1;" % name

        cursor.execute(sql)

        db.commit()
        cursor.close()
        db.close()
    except:
        pass
if __name__=='__main__':
    # 给出提示信息：djangoapp_microblog or djangoapp_wechat
    name = input("请输入要重新爬取的数据表：")
    fun(name)