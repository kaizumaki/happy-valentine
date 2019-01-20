import mysql.connector
from mysql.connector import errorcode
import os
from dotenv import load_dotenv
from sklearn.feature_extraction.text import CountVectorizer
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


def vectorizer_analysis_interval(previous_time, interval_seconds):
    now = datetime.now() + timedelta(hours=9)
    previous = datetime.strptime(previous_time, "%Y-%m-%d %H:%M:%S")
    current_time = previous + timedelta(seconds=interval_seconds)
    while current_time < now:
        print(previous_time, current_time)
        mecabed_data = get_mecabed_data(previous_time, current_time)
        if mecabed_data[0] is not None:
            vectorizer = CountVectorizer(stop_words=['バレンタイン', '拡散希望', 'https', 'retweet', 'する', 'いる'])
            tfidf_matrix = vectorizer.fit_transform(mecabed_data[0])
            feature_names = vectorizer.get_feature_names()
            doc = 0
            feature_index = tfidf_matrix[doc, :].nonzero()[1]
            tfidf_scores = zip(feature_index, [tfidf_matrix[doc, x] for x in feature_index])
            scored_words = [(feature_names[i], s) for (i, s) in tfidf_scores]

            current = current_time.strftime("%Y-%m-%d-%H-%M-%S")

            csv_file_name = 'html/data_count/' + current + '.csv'
            json_file_name = 'html/data_count/' + current + '.json'
            with open(csv_file_name, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(sorted(scored_words, key=itemgetter(1), reverse=True))

            csvfile = open(csv_file_name, 'r')
            jsonfile = open(json_file_name, 'w')

            fieldnames = ('word', 'score')
            reader = csv.DictReader(csvfile, fieldnames)

            jsonfile.write('{"scored_words":[')
            for i, row in enumerate(reader):
                if i != 0:
                    jsonfile.write(',\n')
                json.dump(row, jsonfile, ensure_ascii=False)
            jsonfile.write(']}')

            previous_time = current_time + timedelta(seconds=1)
            current_time = current_time + timedelta(seconds=interval_seconds)


if __name__ == "__main__":
    # ４時間間隔
    vectorizer_analysis_interval('2019-01-19 00:00:00', 60*240)
