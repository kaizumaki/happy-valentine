import MeCab
from collections import defaultdict
import mysql.connector
from mysql.connector import errorcode
import os
from dotenv import load_dotenv
import unicodedata
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

load_dotenv()

config = {
    'user': os.getenv("MYSQL_USER"),
    'password': os.getenv("MYSQL_PASSWORD"),
    'host': 'db',
    'port': '3307',
    'database': os.getenv("MYSQL_DATABASE"),
    'charset': 'utf8mb4'
}


def get_data():
    try:
        cnx = mysql.connector.connect(**config)

        if cnx.is_connected():
            cursor = cnx.cursor(dictionary=True)
            query = "SELECT id, tweet FROM valentine_tweet WHERE mecabed IS NOT True"
            cursor.execute(query)
            data = cursor.fetchall()

    except errorcode as e:
        print(e)

    cursor.close()
    cnx.close()

    return data


def update_data(tweet_id, wakachi, mecabed):
    try:
        cnx = mysql.connector.connect(**config)

        if cnx.is_connected():
            cursor = cnx.cursor()
            query = "UPDATE valentine_tweet SET wakachi = %s, mecabed = %s WHERE id = %s"
            cursor.execute(query, (wakachi, mecabed, tweet_id))
            cnx.commit()

    except errorcode as e:
        print(e)

    cursor.close()
    cnx.close()

    return


def mecab_analysis(sentence):
    tagger = MeCab.Tagger('-Owakati')
    sentence = sentence.replace('\n', ' ')
    result = tagger.parse(sentence)
    return result


if __name__ == "__main__":
    data = get_data()
    wakachi_list = []
    for row in data:
        res = mecab_analysis(unicodedata.normalize('NFKC', row['tweet']))
        wakachi_list.append(res)
        # update_data(row['id'], res, True)

    # print(wakachi_list)
    if wakachi_list:
        vectorizer = CountVectorizer(stop_words=['バレンタイン'])
        word = vectorizer.fit_transform(wakachi_list)
        vector = word.toarray()
        for word, count in zip(vectorizer.get_feature_names()[:], vector[0, :]):
            print(word, count)
        # tran = vectorizer.transform(wakachi_list)
        # print(terms)
        # print(wakachi_list[0])
        # print(tran.toarray())
        # vectorizer = TfidfVectorizer(stop_words=['バレンタイン'])
        # tfidf = vectorizer.fit_transform(wakachi_list).toarray()
        # feature_names = np.array(vectorizer.get_feature_names())
        # index = tfidf.argsort(axis=1)[:, ::-1]
        # n = 10  # いくつほしいか
        # feature_words = [feature_names[doc[:n]] for doc in index]
        # print(feature_words)
        # terms = vectorizer.get_feature_names()
        # print(terms)
        # print(vectorizer.vocabulary_)
        # for k, v in sorted(vectorizer.vocabulary_.items(), key=lambda x: x[1]):
        #     print(k, v)
