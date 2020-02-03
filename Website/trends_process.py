# -*- coding: utf-8 -*-

import tweepy
from pymongo import MongoClient
from model import Preprocessing
from operator import itemgetter
import pickle
from textblob import TextBlob

MONGO_HOST = 'mongodb://localhost/twittertest'
client = MongoClient(MONGO_HOST)
db = client.twittertest

consumer_key = ''
consumer_secret = ''
access_token = ''
access_secret = ''

class Extract_trends:

    def isEnglish(s):
        try:
            s.encode(encoding='utf-8').decode('ascii')
        except UnicodeDecodeError:
            return False
        else:
            return True

    def download_trends(self):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        # woeid for INDIA 23424848
        db.trends.remove()
        trends1 = api.trends_place(1)
        data = trends1[0]
        trends = data['trends']
        for trend in trends:
            # print(trend)
            volume = trend['tweet_volume']
            if volume is not None:
                rs = Extract_trends.isEnglish(trend['name'])
                if rs:
                    try:
                        db.trends.insert({"_id": trend['name'], "count": trend['tweet_volume']})
                        # print("_id:",trend['name'],"count:",trend['tweet_volume']);
                    except Exception as e:
                        print("\n")
                        print(e)

class trends_download:
    results = ''

    def get_trends(self):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        classifier_f = open("naivebayes.pickle", "rb")
        classifier = pickle.load(classifier_f)
        p1 = Preprocessing()
        trends_download.results = db.trends.find()
        trendlist = []
        for record in trends_download.results:
             trendlist.append(record)
        sortedtrends = sorted(trendlist, key=itemgetter('count'), reverse=True)
        db.trends.remove()

        count = 0
        for record in sortedtrends:
            if count < 10:
                db.trends.insert({"_id": record['_id'], "count": record['count']})
                count += 1
                result1 = "trend" + str(count)
                

        trends_download.results = db.trends.find()
        length = 0
        for record in trends_download.results:
            length += 1
        print(length)
        t_count = 0
        trends_download.results = db.trends.find()
        for record in trends_download.results:
            if t_count <= length:
                t_count += 1
                result1 = "trend" + str(t_count)
                db[result1].remove()
                print(result1)
                tweetCount = 0
                searchQuery = record['_id']
                print(searchQuery)
                for status in tweepy.Cursor(api.search, q=searchQuery, lang="en").items():
                    if tweetCount < 300:
                        try:
                            create = status.created_at
                            tweet_id = status.id
                            text = status.text
                            coord = status.coordinates

                            # tweet = TextBlob(text)
                            # s = 0
                            # for sentence in tweet.sentences:
                            #     if sentence.sentiment.polarity > 0.0:
                            #         s = s + 1 / 2
                            #     elif sentence.sentiment.polarity < 0.0:
                            #         s = s - 1 / 2
                            #     else:
                            #         s = s
                            # if s > 0:
                            #     label = 1
                            # elif s < 0:
                            #     label = -1
                            # else:
                            #     label = 0

                            strtext = p1.urlremoval(text)
                            str1 = p1.punctuationremoval(strtext)
                            str2 = p1.lowercase(str1)
                            words = p1.stopwordRemoval(str2)
                            words = p1.stemming(words)
                            p1.extract_feature_dict()
                            label = classifier.classify(p1.get_extracted_features(words))

                            post = {"_id": tweet_id, "created_at": create, "text": text, "coordinates": coord, "sentiment": label}
                            db[result1].insert(post)
                            tweetCount += 1
                        except Exception as e:
                            print("\n")
                            print(e)
                    else:
                        break
                print("Downloaded {0} tweets".format(tweetCount))
            else:
                break
        client.close()

def main():
    et = Extract_trends()
    et.download_trends()
    print("Trends downloaded.")
    td = trends_download()
    td.get_trends()
    print("All trends downloaded.")

if __name__ == '__main__':
    main()

