from bokeh.io import output_file, show
from bokeh.models import ( GMapPlot, GMapOptions, ColumnDataSource, DataRange1d, Circle, Range1d, PanTool, WheelZoomTool, BoxSelectTool, ResetTool)
import ipywidgets as wid
from IPython.core.display import display
import pandas as pd
import numpy as np
from bokeh.plotting import figure, save
from bokeh.models import HoverTool
from bokeh.models.renderers import *
from io import BytesIO
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.plotting import figure
from bokeh.transform import factor_cmap
import matplotlib.pyplot as plt
from os import path
from scipy.misc import imread
import random
from wordcloud import WordCloud, STOPWORDS
from pymongo import MongoClient
import random
from model import Preprocessing

class graph:
    
    def __init__(self):
        #for color dictionary of main page
        MONGO_HOST = 'mongodb://localhost/twittertest'
        client = MongoClient(MONGO_HOST)
        db = client.twittertest

        result = db.trends.find()
        id = 0
        self.titles = []
        self.count = []
        self.pos_count = []
        self.neg_count = []
        self.neut_count = []
        self.total_count = []

        for record in result:
            id += 1
            result1 = "trend" + str(id)
            t = record["_id"]
            self.titles.append(t)
            c = record ["count"]
            self.count.append(c)
            pos = db[result1].find({"sentiment": 1}).count()
            self.pos_count.append(pos)
            neut = db[result1].find({"sentiment": 0}).count()
            self.neut_count.append(neut)
            neg = db[result1].find({"sentiment": -1}).count()
            self.neg_count.append(neg)
            total = pos + neut + neg
            self.total_count.append(total)    
        
        self.topics = []
        self.tweets = []
        self.sent_value = []
        self.coord_x = []
        self.coord_y = []
        id = 0
        self.colors = []
        result = db.trends.find()
        for record in result:
            id+=1;
            result1 = "trend" + str(id)
            t = record["_id"]
            re = db[result1].find()
            for record1 in re:
                self.topics.append(t)
                self.tweets.append(record1["text"])
                self.sent_value.append(record1["sentiment"])
                self.coord_x.append(random.uniform(0,73))
                self.coord_y.append(random.uniform(0,150))

        client.close()  

        self.color_dict = ['#37AB65', '#3DF735', '#AD6D70', '#EC2504', '#8C0B90', '#C0E4FF', '#27B502', '#7C60A8', '#CF95D7', '#F6CC1D']
        self.data_dict = {}
        self.color_main = []

        for i in range(len(self.titles)):
            self.data_dict[self.titles[i]]=self.color_dict[i]

        for k in self.topics:
            if k in self.data_dict:
                self.color_main.append(self.data_dict[k])

    def pie_chart(self):
        fig, ax = plt.subplots()
        ax.axis('equal')
        mypie, _ = ax.pie(self.count, radius=2, labels=self.titles, colors=self.color_dict )
        pies = ax.pie(self.count, autopct='%1.1f%%',colors=self.color_dict )
        plt.setp( mypie, width=0.6)
        plt.margins(0,0)
        plt.figure(figsize=(1,1))
        plt.background_fill_color = "beige"
        plt.background_fill_alpha = 0.5
        # plt.show()
        fn = "F:\Final Year Project\Visualization\Website\static\main_page\Pie.jpeg"
        #print("Saving '%s'" % fn)
        fig.savefig(fn, bbox_inches='tight', pad_inches=0)
        plt.close()

    def mult_bar_graph(self):
        output_file("F:\Final Year Project\Visualization\Website\static\main_page\mult_bar.html")
        years = ['Pos', 'Neg', 'Neutral']
        data = {'title' : self.titles,
                'pos'   : self.pos_count,
                'neg'   : self.neg_count,
                'neut'   : self.neut_count}
        palette = ["#32CD32", "#FF0000", "#4169E1"]
        x = [ (i, j) for i in self.titles for j in years ]
        counts = sum(zip(self.pos_count, self.neg_count, self.neut_count), ()) # like an hstack
        source = ColumnDataSource(data=dict(x=x, counts=counts))
        p = figure(x_range=FactorRange(*x), plot_height=550,plot_width=900, title="Polarity Count for Top Trending Tweets",
                   toolbar_location=None,tools="")
        p.vbar(x='x', top='counts', width=0.85, source=source, line_width=5,line_dash_offset=15,line_color="white",
               fill_color=factor_cmap('x', palette=palette, factors=years, start=1, end=2))
        p.background_fill_color = "beige"
        p.background_fill_alpha = 0.5
        p.y_range.start = 0
        p.x_range.range_padding = 0.1
        p.xaxis.major_label_orientation = 1
        p.xgrid.grid_line_color = None
        # show(p)
        save(obj=p, filename="F:\Final Year Project\Visualization\Website\static\main_page\mult_bar.html")

    def horizon_bar_graph(self):
        np.random.seed(19680801)
        plt.rcdefaults()
        fig, ax = plt.subplots()
        y_pos = np.arange(len(self.titles))
        performance = 3 + 10 * np.random.rand(len(self.titles))
        error = np.random.rand(len(self.titles))
        ax.barh(y_pos, self.count, xerr=error, align='center',
                color='green', ecolor='black')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(self.titles)
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_xlabel('Tweet Count')
        ax.set_title('')
        # plt.show()
        fn = "F:\Final Year Project\Visualization\Website\static\main_page\graph_bar.jpeg"
        fig.savefig(fn, bbox_inches='tight', pad_inches=0)
        plt.close()

        
    def main_map(self):
        #code for main page map
        for i in range(len(self.titles)):
            self.data_dict[self.titles[i]]=self.color_dict[i]
            
        for k in self.topics:
            if k in self.data_dict:
                self.color_main.append(self.data_dict[k])

        map_options = GMapOptions(lat=23.3468, lng=78.5827, map_type='roadmap', zoom=5)

        my_hover = HoverTool()
        plot = GMapPlot(x_range=Range1d(), y_range=Range1d(), map_options=map_options)
        plot.title.text = "Tweet Data Analysis"
        plot.api_key = "AIzaSyAcvz_u0fGAyBE13pAnntsA1fn7Tu54RTU"

        source = ColumnDataSource(data=dict(lat=self.coord_x,lon=self.coord_y,colors=self.color_main[:len(self.coord_x)],tp=self.topics,tw=self.tweets))
        my_hover.tooltips = [('Topic','@tp'),('Tweet','@{tw}')]

        circle = Circle(x="lon", y="lat", size=8, fill_color="colors", fill_alpha=0.7, line_color=None)
        plot.add_glyph(source, circle)
        plot.add_tools(my_hover)
        plot.add_tools( WheelZoomTool(), PanTool(), ResetTool())
        output_file("F:\Final Year Project\Visualization\Website\static\main_page\map.html")
        save(obj=plot, filename="F:\Final Year Project\Visualization\Website\static\main_page\map.html")
        #show(plot)

    def trend_map(self):
        #code for individual trend maps
        MONGO_HOST = 'mongodb://localhost/twittertest'
        client = MongoClient(MONGO_HOST)
        db = client.twittertest
        i=1
        id = 0
        for t in self.titles:
            id+=1
            self.topics = []
            self.tweets = []
            self.sent_value = []
            self.coord_x = []
            self.coord_y = []
            self.colors = []
            result1 = "trend" + str(id)
            k= 0.001
            l= 0.001
            re = db[result1].find()
            for record1 in re:
                self.topics.append(t)
                self.tweets.append(record1["text"])
                self.sent_value.append(record1["sentiment"])
                self.coord_x.append(random.uniform(0,73))
                self.coord_y.append(random.uniform(0,150))                
                
                for x in self.sent_value:
                    if x==1:
                        self.colors.append('#02818a')
                    elif x==-1:
                        self.colors.append('#FF0000')
                    elif x==0:
                        self.colors.append('#008000')
                k+=0.1
                l+=0.2
            #topic = df_trend['topic']
            sent_str = ""
            p = Preprocessing()
            for j in self.tweets:
                text = p.urlremoval(p.lowercase(j))
                list_tweet = []
                a = p.stopwordRemoval(text)
                list_tweet.append(a)
                for m in list_tweet:
                    sent_str += str(m) + " "
            sent_str = sent_str[:-1]
            self.wordcloud(i,sent_str)
            map_options = GMapOptions(lat=23.3468, lng=78.5827, map_type='roadmap', zoom=5)

            my_hover = HoverTool()
            plot = GMapPlot(x_range=Range1d(), y_range=Range1d(), map_options=map_options)
            plot.title.text = "Tweet Data Analysis"
            plot.api_key = "AIzaSyAcvz_u0fGAyBE13pAnntsA1fn7Tu54RTU"
            source = ColumnDataSource(data=dict(lat=self.coord_x,lon=self.coord_y,colors=self.colors[:len(self.coord_x)],tw=self.tweets))
            my_hover.tooltips = [('Tweet','@{tw}')]

            circle = Circle(x="lon", y="lat", size=8, fill_color="colors", fill_alpha=0.7, line_color=None)
            plot.add_glyph(source, circle)
            plot.add_tools(my_hover)
            plot.add_tools( WheelZoomTool(), PanTool(), ResetTool())
            output_file("F:\Final Year Project\Visualization\Website\static\Trends\\"+str(i)+"\map.html")
            i=i+1
            save(obj=plot, filename="F:\Final Year Project\Visualization\Website\static\Trends\\"+str(i-1)+"\map.html")
            #show(plot)
           
    def trend_pie(self):
            #Program to read data from csv file
            for i in range(1,11):
                p_count = [self.pos_count[i-1],self.total_count[i-1]-self.pos_count[i-1]]
                n_count = [self.neg_count[i-1],self.total_count[i-1]-self.neg_count[i-1]]
                a_count = [self.neut_count[i-1],self.total_count[i-1]-self.neut_count[i-1]]
                color_dict = ['#32CD32','#00FF00' , '#AD6D70', '#FF0000', '#FA8072', '#C0E4FF', '#0000ff', '#9999ff', '#CF95D7', '#F6CC1D']
                fig1, ax1 = plt.subplots()
                fig2, ax2 = plt.subplots()
                fig3, ax3 = plt.subplots()
                ax1.axis('equal')
                ax2.axis('equal')
                ax3.axis('equal')

                mypie1, _ = ax1.pie(p_count, radius=1 ,colors=color_dict[0:2])
                plt.setp( mypie1, width=0.2,linewidth=0)
                ax1.text(0, 0.2, "POS ", ha='center',size=25,color='#32CD32')
                ax1.text(0,-0.3,str(int(self.pos_count[i-1]/self.total_count[i-1]*100))+"%",ha='center',size=25,color='#32CD32')

                mypie2, _ = ax2.pie(n_count, radius=1, colors=color_dict[3:5] )
                plt.setp( mypie2, width=0.2,linewidth=0)
                ax2.text(0, 0.2, "NEG", ha='center',size=25,color='#FF0000')
                ax2.text(0,-0.3,str(int(self.neg_count[i-1]/self.total_count[i-1]*100))+"%",ha='center',size=25,color='#FF0000')

                mypie3, _ = ax3.pie(a_count, radius=1, colors=color_dict[6:8] )
                plt.setp( mypie3, width=0.2,linewidth=0)
                ax3.text(0, 0.2, "NEUT", ha='center',size=25,color='#0000ff')
                ax3.text(0,-0.3,str(int(self.neut_count[i-1]/self.total_count[i-1]*100))+"%",ha='center',size=25,color='#0000ff')

                plt.margins(0,0)
                plt.figure(figsize=(1,1))
                plt.background_fill_color = "beige"
                plt.background_fill_alpha = 0.5
                #plt.show()
                plt.close()
                fn1 = "F:\Final Year Project\Visualization\Website\static\Trends"+"\\"+str(i)+"\Pie_pos.jpeg"
                fn2 = "F:\Final Year Project\Visualization\Website\static\Trends"+"\\"+str(i)+"\Pie_neg.jpeg"
                fn3 = "F:\Final Year Project\Visualization\Website\static\Trends"+"\\"+str(i)+"\Pie_neut.jpeg"

                fig1.savefig(fn1, bbox_inches='tight', pad_inches=0)
                fig2.savefig(fn2, bbox_inches='tight', pad_inches=0)
                fig3.savefig(fn3, bbox_inches='tight', pad_inches=0)

    def wordcloud(self,i,text):
            fig, ax = plt.subplots()
            wordcloud = WordCloud(relative_scaling = 0.4,background_color='white',random_state=1,scale=3,stopwords = self.titles)
            wordcloud.generate(text)
            plt.imshow(wordcloud)
            plt.axis("off")
            fig1 = plt.figure(1,figsize=(7.5,7.5))
            #plt.show()
            plt.close()
            fn = "F:\Final Year Project\Visualization\Website\static\Trends"+"\\"+str(i)+"\wordcloud.jpeg"
            fig.savefig(fn, bbox_inches='tight', pad_inches=0)
