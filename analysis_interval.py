import MeCab
from collections import defaultdict
import mysql.connector
from mysql.connector import errorcode
import os
from dotenv import load_dotenv
import unicodedata
from sklearn.feature_extraction.text import TfidfVectorizer
from operator import itemgetter
from datetime import datetime, timedelta
import csv
import json

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


def get_mecabed_data(previous_time, current_time):
    try:
        cnx = mysql.connector.connect(**config)

        if cnx.is_connected():
            cursor = cnx.cursor()
            query = "SELECT group_concat(t1.mecabed_data separator ' ') FROM tweet_analysis t1 JOIN valentine_tweet t2 ON t1.tweet_id = t2.id WHERE t2.created_at BETWEEN %s AND %s"
            cursor.execute(query, (previous_time, current_time))
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
            query = "INSERT INTO tweet_analysis (tweet_id, part, mecabed_data) VALUES (%s, %s, %s)"
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


def vectorizer_analysis_interval(previous_time, interval_seconds):
    # now = datetime.now() + timedelta(hours=9)
    now = datetime.strptime('2019-02-15 04:33:00', "%Y-%m-%d %H:%M:%S")
    previous = datetime.strptime(previous_time, "%Y-%m-%d %H:%M:%S")
    current_time = previous + timedelta(seconds=interval_seconds)
    while current_time < now:
        print(previous_time, current_time)
        mecabed_data = get_mecabed_data(previous_time, current_time)

        try:
            vectorizer = TfidfVectorizer(stop_words=['バレンタイン', '拡散希望', 'https', 'retweet', 'する', 'いる'])
            tfidf_matrix = vectorizer.fit_transform(mecabed_data[0])
            feature_names = vectorizer.get_feature_names()
            doc = 0
            feature_index = tfidf_matrix[doc, :].nonzero()[1]
            tfidf_scores = zip(feature_index, [tfidf_matrix[doc, x] for x in feature_index])
            scored_words = [(feature_names[i], s) for (i, s) in tfidf_scores]

            current = current_time.strftime("%Y-%m-%d-%H-%M-%S")

            csv_file_name = 'html/data/' + current + '.csv'
            json_file_name = 'html/data/' + current + '.json'
            with open(csv_file_name, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(sorted(scored_words, key=itemgetter(1), reverse=True))

            with open(csv_file_name, 'r', newline='') as f_csv:
                fieldnames = ('word', 'score')
                reader = csv.DictReader(f_csv, fieldnames)
                with open(json_file_name, 'w', newline='') as f_json:
                    f_json.write('{"scored_words":[')
                    for i, row in enumerate(reader):
                        if i != 0:
                            f_json.write(',\n')
                        json.dump(row, f_json, ensure_ascii=False)
                    f_json.write(']}')

            with open('html/data_names.csv', 'a', newline='') as f_name:
                writer = csv.writer(f_name)
                writer.writerow([current])

            with open('html/data_names.csv', 'r', newline='') as f_name_csv:
                data_names_reader = csv.DictReader(f_name_csv, ('filename',))
                with open('html/data_names.json', 'w', newline='') as f_name_json:
                    f_name_json.write('[')
                    for i, row in enumerate(data_names_reader):
                        if i != 0:
                            f_name_json.write(',\n')
                        json.dump(row, f_name_json, ensure_ascii=False)
                    f_name_json.write(']')

        except AttributeError as e:
            print(e)
            print('There are no tweets.')

        previous_time = current_time + timedelta(seconds=1)
        current_time = current_time + timedelta(seconds=interval_seconds)


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

    # ４時間間隔
    vectorizer_analysis_interval('2019-02-06 00:00:00', 60*240)
