import MeCab
from collections import defaultdict
import mysql.connector
from mysql.connector import errorcode
import os
from dotenv import load_dotenv
import unicodedata
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

load_dotenv()

config = {
    'user': os.getenv("MYSQL_USER"),
    'password': os.getenv("MYSQL_PASSWORD"),
    'host': 'db',
    'port': '3306',
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


def get_mecabed_data():
    try:
        cnx = mysql.connector.connect(**config)

        if cnx.is_connected():
            cursor = cnx.cursor()
            query = "SELECT wakachi FROM valentine_tweet WHERE mecabed IS NOT True"
            cursor.execute(query)
            data = cursor.fetchall()

    except errorcode as e:
        print(e)

    cursor.close()
    cnx.close()

    return data


def update_data_wakachi(tweet_id, wakachi):
    try:
        cnx = mysql.connector.connect(**config)

        if cnx.is_connected():
            cursor = cnx.cursor()
            query = "UPDATE valentine_tweet SET wakachi = %s WHERE id = %s"
            cursor.execute(query, (wakachi, tweet_id))
            cnx.commit()

    except errorcode as e:
        print(e)

    cursor.close()
    cnx.close()

    return


def update_data_mecabed(tweet_id, mecabed):
    try:
        cnx = mysql.connector.connect(**config)

        if cnx.is_connected():
            cursor = cnx.cursor()
            query = "UPDATE valentine_tweet SET mecabed = %s WHERE id = %s"
            cursor.execute(query, (mecabed, tweet_id))
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
        update_data_wakachi(row['id'], res)

    mecabed_data = get_mecabed_data()
    print(wakachi_list)
    # if mecabed_data[0] is not None:
    vectorizer = TfidfVectorizer(stop_words=['バレンタイン'])
    tfidf = vectorizer.fit_transform(wakachi_list).toarray()
    feature_names = np.array(vectorizer.get_feature_names())
    index = tfidf.argsort(axis=1)[:, ::-1]
    n = 10  # いくつほしいか
    feature_words = [feature_names[doc[:n]] for doc in index]
    print(feature_words)
    # terms = vectorizer.get_feature_names()
    # print(vectorizer.vocabulary_)
    # for row in data:
    #     mecabed = True
    #     update_data_mecabed(row['id'], mecabed)
