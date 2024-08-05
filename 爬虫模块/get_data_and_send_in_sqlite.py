import sqlite3
import time
import random
import urllib.request
import urllib.response
import urllib.parse
import re
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool

findBrand = re.compile(r'<a href=".*">(.*?)<!--')  # 爬取品牌的正则表达式
findModel = re.compile(r'<h1>(.*?)</h1>')  # 爬取车型的正则表达式
findScore = re.compile(r'<em class="">(\d\.\d+)</em>')  # 爬取评分的正则表达式
findPrice = re.compile(r'(\d+\.\d+)')  # 爬取价格的正则表达式
findRemark = re.compile(r'<div>(.*?)<!--')  # 爬取评价内容（正负面评价通用式）
findRemarkScore = re.compile(r'-->(\d+)</div>')  # 爬取评价评分（正负面评分通用式）
findImg = re.compile(r'<img alt="" src="(.*?)"')  # 爬取车辆图片


def load_user_agents():  # 从user_agents.txt里面获取user_agent并打乱顺序，防封
    uas = []
    with open("user_agents.txt", 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[1:-1])
    random.shuffle(uas)
    return uas


def load_valid_url():  # 获取待爬取的url
    url_list = []  # 用来存放待爬取的url
    with open("valid_url_list.txt", "r") as f:
        for url in f.readlines():
            if url:
                url_list.append(url.replace("www", 'k').strip())
    return url_list


def get_html(url):  # 获取指定url的html
    user_agent = random.choice(user_agent_list)
    headers = {"User-Agent": user_agent}
    request = urllib.request.Request(url=url, headers=headers)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html


def get_data(url):  # 从单个url中获取数据（为了实现多线程处理不能传url列表）
    html = get_html(url)
    soup = BeautifulSoup(html, "html.parser")

    # 爬取评分
    div = str(soup.find("div", class_="score_star__yBrf7"))  # 爬取评分
    score_list = re.findall(findScore, div)
    if not score_list:  # 评分为空的车型我们选择不计入
        return
    score = str(score_list[0])

    # 爬取售价
    div = str(soup.find_all("div", class_="score_con__part__7sGtJ")[1])
    price_list = re.findall(findPrice, div)
    if not price_list:
        return  # 售价为空的车型我们选择不计入
    elif len(price_list) == 2:
        # 对售价区间我们选择取平均值记录
        price = str("{:.2f}".format((float(price_list[0]) + float(price_list[1])) / 2))
    else:
        price = str(price_list[0])

    # 爬取正负面评价内容及其评分
    li_positive = str(soup.select('ul[class="score_tag__Wq2Z4"] > li[class=""]'))
    positive_remark_list = re.findall(findRemark, li_positive)
    positive_remark_list_str = " ".join(positive_remark_list)  # 列表转字符串并用空格隔开

    positive_score_list = re.findall(findRemarkScore, li_positive)
    positive_score_list_str = " ".join(positive_score_list)

    li_negative = str(soup.select('ul[class="score_tag__Wq2Z4"] > li[class="score_grey__qIDN7"]'))
    negative_remark_list = re.findall(findRemark, li_negative)
    negative_remark_list_str = " ".join(negative_remark_list)

    negative_score_list = re.findall(findRemarkScore, li_negative)
    negative_score_list_str = " ".join(negative_score_list)

    # 爬取品牌与车型
    div = str(soup.find("div", class_="header_toolbar__car__name__5SxJb"))
    brand = re.findall(findBrand, div)[0]  # 爬取品牌
    model = re.findall(findModel, div)[0]  # 爬取车型

    # 爬取车辆图片
    div = str(soup.find("div", class_="score_carimg__Z_18d"))
    img_link = "https:" + re.findall(findImg, div)[0]

    # 数据打包
    datalist.append([brand, model, price, score,
                 positive_remark_list_str, positive_score_list_str,
                 negative_remark_list_str, negative_score_list_str,
                 img_link])


def save_data_to_db(datalist):  # 将获取的datalist传进数据库
    conn = sqlite3.connect("../database.db")
    cursor = conn.cursor()
    for data in datalist:
        for index in range(len(data)):  # 给取出的字符串数据加""前后缀，方便传入数据库
            if index == 2 or index == 3:  # 若当前数据为price或index则跳过加双引号的操作
                continue
            data[index] = '"' + data[index] + '"'
        sql = '''
            insert into Car(
                brand, model, price, score, 
                positive_remark, positive_score, 
                negative_remark, negative_score, img) values(%s)
                ''' % ",".join(data)
        cursor.execute(sql)
        conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    global datalist
    datalist = []
    global user_agent_list

    user_agent_list = load_user_agents()  # 获取user_agent列表
    valid_url_list = load_valid_url()

    pool = Pool(10)  # 多线程爬取
    pool.map(get_data, valid_url_list)  # 为了防封，建议分段爬取

    save_data_to_db(datalist)
