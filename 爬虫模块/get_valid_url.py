import time
import random
import urllib.request
import urllib.response
import urllib.parse
from multiprocessing.dummy import Pool


def load_user_agents():  # 从user_agents.txt文件里面获取user_agent列表，防封
    uas = []
    with open("user_agents.txt", 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[1:-1 - 1])
    random.shuffle(uas)
    return uas


def get_valid_html(url):  # 找到车型网页并记录在valid_url_list.txt中
    user_agent = random.choice(user_agent_list)  # 从user_agent列表中随机抽一个user_agent
    headers = {"User-Agent": user_agent}
    request = urllib.request.Request(url=url, headers=headers)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("gbk")
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    if html[0] == "车":  # 爬取的页面若无车型则直接返回
        time.sleep(random.uniform(1, 3))  # 自定义随机睡眠时间，防封
        return
    else:  # 若有车型则记录该url
        time.sleep(random.uniform(1, 3))  # 自定义随机睡眠时间，防封
        with open('valid_url_list.txt', 'a', encoding='utf-8') as f:
            f.write(url + '\n')


if __name__ == "__main__":
    global user_agent_list
    user_agent_list = load_user_agents()  # 获取user_agent列表

    # 为了防止被检测封IP，不能一次性爬1-8000号车辆，建议分段爬取
    url = ["https://www.autohome.com.cn/" + str(i) for i in range(1, 8001)]
    print(url)

    # 多线程爬取
    pool = Pool(10)
    pool.map(get_valid_html, url)
