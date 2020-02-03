from flask import Flask, render_template
import pandas as pd
from Graph import graph 
from pymongo import MongoClient
import matplotlib.pyplot as plt

MONGO_HOST = 'mongodb://localhost/twittertest'
client = MongoClient(MONGO_HOST)
db = client.twittertest

result = db.trends.find()
id = 0
titles = []
count = []
pos_count = []
neg_count = []
neut_count = []
total_count = []
topics = []
tweets = []
sent_value = []

for record in result:
   id += 1
   result1 = "trend" + str(id)
   t = record["_id"]
   titles.append(t)
   c = record ["count"]
   count.append(c)
   pos = db[result1].find({"sentiment": 1}).count()
   pos_count.append(pos)
   neut = db[result1].find({"sentiment": 0}).count()
   neut_count.append(neut)
   neg = db[result1].find({"sentiment": -1}).count()
   neg_count.append(neg)
   total = pos + neut + neg
   total_count.append(total)    

result = db.trends.find()
id = 0
for record in result:
   id+=1;
   result1 = "trend" + str(id)
   t = record["_id"]
   re = db[result1].find()
   for record1 in re:
      topics.append(t)
client.close()  

g = graph()
app = Flask(__name__)
trend=[1,1,1,1]
main_list = []
k = [1,2,3,4,5,6,7,8,9,10]
main_list.append(k)
main_list.append(titles)
g.pie_chart()
g.mult_bar_graph()
g.horizon_bar_graph()
g.main_map()
g.trend_map()
g.trend_pie()
plt.close('all')
@app.template_global(name='zip')
def _zip(*args, **kwargs): #to not overwrite builtin zip in globals
    return __builtins__.zip(*args, **kwargs)

@app.route('/main')
def result():
   return render_template('main.html', result = zip(k,titles))

@app.route('/trend/<int:name>')
def success(name):
   tweets = []
   trend[0] = (str(name))
   trend[1] = (titles[name-1])
   trend[2] = (count[name-1])
   result1 = "trend" + str(name)
   re = db[result1].find()
   for record1 in re:
      tweets.append(record1["text"])            
      sent_value.append(record1["sentiment"])
   trend[3] = tweets
   
   return render_template('trend.html', result = trend)

if __name__ == '__main__':
    #app.run(use_reloader=True, debug=True,host = '10.12.0.57',port=5005)
    app.run(use_reloader=True, debug=True)
