import mysql.connector
from mysql.connector import errorcode
import tweepy
import json
import datetime
import pytz
import os
from dotenv import load_dotenv
import subprocess

load_dotenv()

config = {
    'user': os.getenv("MYSQL_USER"),
    'password': os.getenv("MYSQL_PASSWORD"),
    'host': 'db',
    'port': '3307',
    'database': os.getenv("MYSQL_DATABASE"),
    'charset': 'utf8mb4'
}


def str_to_date_jp(str_date):
    dts = datetime.datetime.strptime(str_date, '%a %b %d %H:%M:%S +0000 %Y')
    return pytz.utc.localize(dts).astimezone(pytz.timezone('Asia/Tokyo'))


def connect(username, created_at, tweet):
    try:
        cnx = mysql.connector.connect(**config)

        if cnx.is_connected():
            cursor = cnx.cursor()
            query = "INSERT INTO valentine_tweet (username, created_at, tweet) VALUES (%s, %s, %s)"
            cursor.execute(query, (username, created_at, tweet))
            cnx.commit()

    except errorcode as e:
        print(e)

    cursor.close()
    cnx.close()

    return


# Tweepy class to access Twitter API
class Streamlistener(tweepy.StreamListener):

    def on_connect(self):
        print("You are connected to the Twitter API")

    def on_error(self, status_code):
        if status_code != 200:
            print("error found")
            # returning false disconnects the stream
            return False

    """
    This method reads in tweet data as Json
    and extracts the data we want.
    """

    def on_data(self, data):

        try:
            raw_data = json.loads(data)

            if 'text' in raw_data:

                username = raw_data['user']['screen_name']
                created_at = str_to_date_jp(raw_data['created_at'])
                tweet = raw_data['text']

                # insert data just collected into MySQL database
                connect(username, created_at, tweet)
                print("Tweet colleted at: {} ".format(str(created_at)))

        except errorcode as e:
            print(e)


if __name__ == '__main__':
    # # #Allow user input
    # track = []
    # while True:

    # 	input1  = input("what do you want to collect tweets on?: ")
    # 	track.append(input1)

    # 	input2 = input("Do you wish to enter another word? y/n ")
    # 	if input2 == 'n' or input2 == 'N':
    # 		break

    # print("You want to search for {}".format(track))
    # print("Initialising Connection to Twitter API....")
    # time.sleep(2)

    # authentification so we can access twitter
    auth = tweepy.OAuthHandler(os.getenv("TWITTER_CONSUMER_KEY"), os.getenv("TWITTER_CONSUMER_SECRET"))
    auth.set_access_token(os.getenv("TWITTER_ACCESS_TOKEN"), os.getenv("TWITTER_TOKEN_SECRET"))
    api = tweepy.API(auth, wait_on_rate_limit=True)

    # create instance of Streamlistener
    listener = Streamlistener()
    stream = tweepy.Stream(auth=api.auth, listener=listener)
    track = ['バレンタイン', '義理チョコ']
    stream.filter(track=track, languages=['ja'])

    command = ["python", "analysis.py"]
    subprocess.Popen(command)
