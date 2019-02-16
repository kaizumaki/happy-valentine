import mysql.connector
from mysql.connector import errorcode
import os
from dotenv import load_dotenv
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


def vectorizer_analysis_corpus(previous_time, interval_seconds):
    # now = datetime.now() + timedelta(hours=9)
    now = datetime.strptime('2019-02-15 04:33:00', "%Y-%m-%d %H:%M:%S")
    previous = datetime.strptime(previous_time, "%Y-%m-%d %H:%M:%S")
    current_time = previous + timedelta(seconds=interval_seconds)
    corpus = []
    current_time_list = []
    while current_time < now:
        print(previous_time, current_time)
        mecabed_data = get_mecabed_data(previous_time, current_time)
        mecabed_words = list(mecabed_data[0])
        corpus.append(mecabed_words[0])
        current_time_list.append(current_time)

        previous_time = current_time + timedelta(seconds=1)
        current_time = current_time + timedelta(seconds=interval_seconds)

    vectorizer = TfidfVectorizer(stop_words=['バレンタイン', '拡散希望', 'https', 'retweet', 'する', 'いる'])
    tfidf_matrix = vectorizer.fit_transform(corpus)
    feature_names = vectorizer.get_feature_names()
    for doc, obj in enumerate(corpus):
        feature_index = tfidf_matrix[doc, :].nonzero()[1]
        tfidf_scores = zip(feature_index, [tfidf_matrix[doc, x] for x in feature_index])
        scored_words = [(feature_names[i], s) for (i, s) in tfidf_scores]

        current = current_time_list[doc].strftime("%Y-%m-%d-%H-%M-%S")

        csv_file_name = 'html_new/data/' + current + '.csv'
        json_file_name = 'html_new/data/' + current + '.json'
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

        with open('html_new/data_names.csv', 'a', newline='') as f_name:
            writer = csv.writer(f_name)
            writer.writerow([current])


if __name__ == "__main__":
    try:
        # 4時間間隔
        vectorizer_analysis_corpus('2019-02-09 00:00:00', 60*240)

        with open('html_new/data_names.csv', 'r', newline='') as f_name_csv:
            data_names_reader = csv.DictReader(f_name_csv, ('filename',))
            with open('html_new/data_names.json', 'w', newline='') as f_name_json:
                f_name_json.write('[')
                for i, row in enumerate(data_names_reader):
                    if i != 0:
                        f_name_json.write(',\n')
                    json.dump(row, f_name_json, ensure_ascii=False)
                f_name_json.write(']')

    except AttributeError as e:
        print(e)
        print('There are no tweets.')
