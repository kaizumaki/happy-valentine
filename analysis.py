import MeCab
from collections import defaultdict
import mysql.connector
from mysql.connector import errorcode
import os
from dotenv import load_dotenv
import unicodedata
from sklearn.feature_extraction.text import TfidfVectorizer

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
            query = "SELECT group_concat(analysis_data separator ' ') FROM tweet_analysis WHERE part = '名詞'"
            cursor.execute(query)
            data = cursor.fetchall()

    except errorcode as e:
        print(e)

    cursor.close()
    cnx.close()

    return data


def insert_data(tweet_id, part, analysis_data):
    try:
        cnx = mysql.connector.connect(**config)

        if cnx.is_connected():
            cursor = cnx.cursor()
            query = "INSERT INTO tweet_analysis (tweet_id, part, analysis_data) VALUES (%s, %s, %s)"
            cursor.execute(query, (tweet_id, part, analysis_data))
            cnx.commit()

    except errorcode as e:
        print(e)

    cursor.close()
    cnx.close()

    return


def update_data(tweet_id, mecabed):
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
    tagger = MeCab.Tagger('-Ochasen')
    sentence = sentence.replace('\n', ' ')
    node = tagger.parseToNode(sentence)
    result_dict = defaultdict(list)
    while node:
        if node.surface != '':
            word_type = node.feature.split(',')[0]
            if word_type in ['名詞', '動詞', '形容詞', '副詞']:
                plain_word = node.feature.split(',')[6]
                if plain_word != '*':
                    result_dict[word_type].append(plain_word)
        node = node.next
        if node is None:
            break
    return result_dict


if __name__ == "__main__":
    data = get_data()
    for row in data:
        res = mecab_analysis(unicodedata.normalize('NFKC', row['tweet']))

        for key in res.keys():
            if key == '名詞':
                noun_list = []
                for word in res[key]:
                    noun_list.append(word)
                noun_data = ' '.join(noun_list)
                insert_data(row['id'], '名詞', noun_data)
            elif key == '動詞':
                verb_list = []
                for word in res[key]:
                    verb_list.append(word)
                verb_data = ' '.join(verb_list)
                insert_data(row['id'], '動詞', verb_data)
            elif key == '形容詞':
                adjective_list = []
                for word in res[key]:
                    adjective_list.append(word)
                adjective_data = ' '.join(adjective_list)
                insert_data(row['id'], '形容詞', adjective_data)
            elif key == '副詞':
                adverb_list = []
                for word in res[key]:
                    adverb_list.append(word)
                adverb_data = ' '.join(adverb_list)
                insert_data(row['id'], '副詞', adverb_data)

        mecabed = True
        update_data(row['id'], mecabed)

    mecabed_data = get_mecabed_data()
    print(mecabed_data)
    vectorizer = TfidfVectorizer(stop_words=['バレンタイン'])
    tfidf = vectorizer.fit_transform(mecabed_data[0])
    print(tfidf)
    terms = vectorizer.get_feature_names()
    print(terms)
