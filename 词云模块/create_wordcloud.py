import sqlite3
import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from PIL import Image
import numpy as np

conn = sqlite3.connect('../database.db')
cur = conn.cursor()
sql = "select positive_remark from Car"
positives = cur.execute(sql)
sql = "select negative_remark from Car"
negatives = cur.execute(sql)
text = ""
for i in positives:
    text += i[0]
for i in negatives:
    text += i[0]
cur.close()
conn.close()

# 用jieba分词
cut = jieba.cut(text)
string = list(cut)
# 剔除停用词
stopwords = [line.strip() for line in open('D:/datasets/stop_words.txt', encoding='UTF-8').readlines()]
new_string = []
for word in string:
    if word not in stopwords:
        new_string.append(word)
new_string = ' '.join(new_string)


# 构建词云
img = Image.open("tree.jpg")
img_array = np.array(img)
wc = WordCloud(
    background_color='white',
    mask=img_array,
    font_path="msyh.ttc"
)
wc.generate_from_text(new_string)


# 绘制图片
fig = plt.figure(1)
plt.imshow(wc)
plt.axis('off')
plt.savefig("../static/assets/img/wordcloud.jpg", dpi=2000)
