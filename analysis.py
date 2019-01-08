import MeCab
from collections import defaultdict
import unicodedata
import mysql.connector
from mysql.connector import errorcode
import os
from dotenv import load_dotenv

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

    return data


def insert_data(tweet_id, noun, verb, adjective, adverb):
    try:
        cnx = mysql.connector.connect(**config)

        if cnx.is_connected():
            cursor = cnx.cursor()
            query = "INSERT INTO tweet_analysis (tweet_id, noun, verb, adjective, adverb) VALUES (%s, %s, %s, %s, %s)"
            # query = "UPDATE valentine SET noun = %s, verb = %s, adjective = %s, adverb = %s WHERE id = %s"
            cursor.execute(query, (tweet_id, noun, verb, adjective, adverb))
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

        # noun_list = []
        # verb_list = []
        # adjective_list = []
        # adverb_list = []

        for key in res.keys():
            if key == '名詞':
                noun_list = []
                for word in res[key]:
                    noun_list.append(word)
                print(noun_list)
                # tweetdata.update({'_id': d['_id']}, {'$push': {'noun': {'$each': noun_list}}})
            elif key == '動詞':
                verb_list = []
                for word in res[key]:
                    verb_list.append(word)
                # tweetdata.update({'_id': d['_id']}, {'$push': {'verb': {'$each': verb_list}}})
            elif key == '形容詞':
                adjective_list = []
                for word in res[key]:
                    adjective_list.append(word)
                # tweetdata.update({'_id': d['_id']}, {'$push': {'adjective': {'$each': adjective_list}}})
            elif key == '副詞':
                adverb_list = []
                for word in res[key]:
                    adverb_list.append(word)
                # tweetdata.update({'_id': d['_id']}, {'$push': {'adverb': {'$each': adverb_list}}})

        mecabed = True
        # tweetdata.update({'_id': d['_id']}, {'$set': {'mecabed': True}})
        # insert_data(row['id'], noun_list, verb_list, adjective_list, adverb_list, mecabed)
        # print(noun_list)
