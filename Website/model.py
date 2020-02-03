import pickle
from textblob import TextBlob
import re
from pymongo import MongoClient
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag
import nltk
import csv

class Preprocessing:
    results = ''
    db = ''
    feature_list = []

    def connection(self):
        client = MongoClient('localhost', 27017)
        Preprocessing.db = client.twittertest
        Preprocessing.results = Preprocessing.db.dataset.find()
        client.close()

    def lowercase(self, str):
        str = str.lower()
        result = re.sub(r"rt ", "", str)
        result = re.sub(r"amp\w*", "", result)
        result = re.sub(r"\b\d+\b", "", result)
        result = re.sub(r"  ", " ", result)
        # print(result)
        return result

    def urlremoval(self,str):
        result = re.sub(r"http\S+", "", str)
        # print(result)
        return result

    def punctuationremoval(self,str):
        punctuations = '''!()-[]{};:'"|\,<>./?@+#$%^&*_~'''
        no_punct = ""
        for char in str:
            if char not in punctuations:
                no_punct = no_punct + char
        return no_punct

    def spellingcorrect(self,str):
        str_op = TextBlob(str)
        result = str_op.correct()
        return result

    def stopwordRemoval(self,str):
        stop_words = set(stopwords.words('english '))
        word_tokens = word_tokenize(str)
        filtered_sentence = []
        for w in word_tokens:
            if w not in stop_words:
                filtered_sentence.append(w)
        return filtered_sentence

    def postagging(self,words):
        tokens_pos = pos_tag(words)
        print(tokens_pos)

    def stemming(self,words):
        filtered_sentence = []
        for t in words:
            filtered_sentence.append(t)
        return filtered_sentence

    def extract_feature_dict(self):
        with open("unigrams.csv", 'r') as incsv:
            reader = csv.reader(incsv, delimiter=',', quotechar='|')
            counter=0
            for row in reader:
                if counter<=450:
                    Preprocessing.feature_list.append(row[0])
                    counter += 1
                else:
                    break

        with open("ngrams.csv", 'r') as incsv:
            reader = csv.reader(incsv, delimiter=',', quotechar='|')
            for row in reader:
                if counter<=200:
                    Preprocessing.feature_list.append(row[0])
                    counter += 1
                else:
                    break

        #print(len(Preprocessing.feature_list))
        #print(Preprocessing.feature_list)

    def get_extracted_features(self,words):
        features = {}
        for word in words:
            if word in Preprocessing.feature_list:
                features[word] = 1
        #print(features)
        return features

def main():
    all_tweets = []
    p1 = Preprocessing()
    p1.connection()
    unigrams_fd = nltk.FreqDist()
    n_grams_fd = nltk.FreqDist()
    count = 0
    for record in p1.results:
        if count<21604:
            str = p1.urlremoval(record['text'])
            str1 = p1.punctuationremoval(str)
            str2 = p1.lowercase(str1)
            words = p1.stopwordRemoval(str2)
            words = p1.stemming(words)
            all_tweets.append((words, record['sentiment']))
            unigrams_fd.update(words)
            words_bi = [' '.join(map(''.join, bg)) for bg in nltk.bigrams(words)]
            n_grams_fd.update(words_bi)
            words_tri = [' '.join(map(''.join, tg)) for tg in nltk.trigrams(words)]
            n_grams_fd.update(words_tri)
            count += 1
        else:
            break

    unigrams_sorted = [(k,v) for (k, v) in unigrams_fd.items() if v > 25]
    unigrams_sorted1 = sorted(unigrams_sorted, key=lambda s: s[1], reverse=True)
    with open ("unigrams.csv", 'w') as outcsv:
        writer = csv.writer(outcsv, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writer.writerow(['word','freq'])
        for item in unigrams_sorted1:
            if (len(item[0]) > 2):
                writer.writerow([item[0], item[1]])

    ngrams_sorted = [(k,v) for (k, v) in n_grams_fd.items() if v > 25]
    ngrams_sorted1 = sorted(ngrams_sorted, key=lambda s: s[1], reverse=True)
    with open("ngrams.csv", 'w') as outcsv:
        writer = csv.writer(outcsv, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writer.writerow(['word','freq'])
        for item in ngrams_sorted1:
            if(len(item[0])>2):
                writer.writerow([item[0], item[1]])

    p1.extract_feature_dict()

    # print(all_tweets)
    train_tweets = [x for i, x in enumerate(all_tweets) if i % 5 != 0]
    test_tweets = [x for i, x in enumerate(all_tweets) if i % 5 == 0]
    v_train = nltk.classify.apply_features(p1.get_extracted_features, train_tweets)
    v_test = nltk.classify.apply_features(p1.get_extracted_features, test_tweets)
    # print(train_tweets)
    # print(test_tweets)

    CLASSIFIER = nltk.classify.NaiveBayesClassifier
    classifier_tot = CLASSIFIER.train(v_train)
    accuracy_tot = nltk.classify.accuracy(classifier_tot, v_test)
    print('Accuracy :', accuracy_tot)

    save_classifier = open("naivebayes1.pickle", "wb")
    pickle.dump(classifier_tot, save_classifier)
    save_classifier.close()

    test_truth = [s for (t, s) in v_test]
    test_predict = [classifier_tot.classify(t) for (t, s) in v_test]
    print('Confusion Matrix')
    print(nltk.ConfusionMatrix(test_truth, test_predict))

    #  CLASSIFIER = nltk.classify.MaxentClassifier
    #  classifier_tot1 = CLASSIFIER.train(v_train, algorithm='GIS', max_iter=10)
    #  accuracy_tot1 = nltk.classify.accuracy(classifier_tot1, v_test)
    #  print('Accuracy :', accuracy_tot1)

    # CLASSIFIER =  nltk.classify.SklearnClassifier(LinearSVC())
    # classifier_tot2 = CLASSIFIER.train(v_train)
    # accuracy_tot2 = nltk.classify.accuracy(classifier_tot2, v_test)
    # print('Accuracy :', accuracy_tot2)

    # CLASSIFIER = nltk.classify.DecisionTreeClassifier
    # classifier_tot = CLASSIFIER.train(v_train, entropy_cutoff=0.05, depth_cutoff=100, support_cutoff=10, binary=False)
    # accuracy_tot = nltk.classify.accuracy(classifier_tot, v_test)
    # print('Accuracy :', accuracy_tot)

if __name__ == '__main__':
    main()
