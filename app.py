import sqlite3
from flask import Flask, render_template, request
app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/index")
def home():
    return index()


@app.route("/car_info", methods=["POST", "GET"])  # 车辆信息
def car_info():
    datalist = []
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    if request.method == "POST":  # 如果methods是post，我们可以拿到表单上的所有内容
        result = request.form
        for x, y in result.items():
            name = x
            keyword = '"' + y + '"'  # keyword里存放用户输入的值
        sql = "select * from Car where brand = %s or model = %s" % (keyword, keyword)
        data = cur.execute(sql)
        for i in data:
            datalist.append(i)
        cur.close()
        conn.close()
        return render_template("car_info.html", cars=datalist)
    sql = "select * from Car"
    data = cur.execute(sql)
    for i in data:
        datalist.append(i)
    cur.close()
    conn.close()
    return render_template("car_info.html", cars=datalist)


@app.route("/market_share")  # 品牌占比
def market_share():
    brands_and_nums = []
    # 记录品牌和车型数量。因为jinja2不支持多变量迭代只能将两个数据装入一个列表中（也可能支持但我不会）

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    sql = '''select brand, count(brand) from Car group by brand 
    order by count(brand) desc'''  # 按照品牌车型数量降序排序
    data = cur.execute(sql)
    for i in data:
        brands_and_nums.append(i)
    cur.close()
    conn.close()
    return render_template("market_share.html", brands_and_nums=brands_and_nums[:50])
    # 我们只选数量最多的前50个品牌看


@app.route("/car_price")  # 车型价格及品牌均价
def car_price():
    model = []  # 记录车型
    model_price = []  # 记录车型价格
    brand = []  # 记录品牌
    brand_average_price = []  # 记录品牌均价
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # 获取品牌平均售价
    sql = "select model, price from Car"
    data = cur.execute(sql)
    for i in data:
        model.append(i[0])
        model_price.append(i[1])

    # 获取所有车型售价
    sql = "select brand, avg(price) from Car group by brand"
    data = cur.execute(sql)
    for i in data:
        brand.append(i[0])
        brand_average_price.append(float("{:.2f}".format(i[1])))
    cur.close()
    conn.close()
    return render_template("car_price.html", model=model, model_price=model_price,
                           brand=brand, brand_average_price=brand_average_price)


@app.route("/car_score")  # 车型评分及品牌均分
def car_score():
    model = []  # 记录车型
    model_score = []  # 记录车型评分
    brand = []  # 记录品牌
    brand_average_score = []  # 记录品牌均分
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # 获取所有车型评分
    sql = "select model, score from Car"
    data = cur.execute(sql)
    for i in data:
        model.append(i[0])
        model_score.append(i[1])

    # 获取所有品牌均分
    sql = "select brand, avg(score) from Car group by brand"
    data = cur.execute(sql)
    for i in data:
        brand.append(i[0])
        brand_average_score.append(float("{:.2f}".format(i[1])))
    cur.close()
    conn.close()
    return render_template("car_score.html", model=model, model_score=model_score,
                           brand=brand, brand_average_score=brand_average_score)


@app.route("/car_remark", methods=["POST", "GET"])
def car_remark():
    models = []
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    sql = "select model from Car"
    data = cur.execute(sql)
    for i in data:
        models.append(i)
    if request.method == "POST":  # 如果methods是post，我们可以拿到表单上的所有内容
        result = request.form
        for x, y in result.items():
            name = x
            keyword = '"' + y + '"'  # keyword里存放用户输入的值
        sql = "select * from Car where model = %s" % keyword
        data = cur.execute(sql)
        for i in data:
            positive_remark = i[5].split()
            positive_score = i[6].split()
            negative_remark = i[7].split()
            negative_score = i[8].split()
        positives = list(zip(positive_remark, positive_score))
        negatives = list(zip(negative_remark, negative_score))
        cur.close()
        conn.close()
        return render_template("car_remark.html", positives=positives, negatives=negatives, models=models)
    return render_template("car_remark.html", positives=[], models=models)


@app.route("/wordcloud")
def wordcloud():
    return render_template("wordcloud.html")


if __name__ == '__main__':
    app.run(debug=True)
