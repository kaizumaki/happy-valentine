import mysql.connector
from mysql.connector import errorcode
import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("MYSQL_DATABASE")

TABLES = {}
TABLES['valentine_tweet'] = (
    "CREATE TABLE `valentine_tweet` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `username` varchar(255) NOT NULL,"
    "  `created_at` date NOT NULL,"
    "  `tweet` text NOT NULL,"
    "  `mecabed` enum('True','False'),"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")
TABLES['tweet_analysis'] = (
    "CREATE TABLE `tweet_analysis` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `tweet_id` int(11) NOT NULL,"
    "  `noun` varchar(255),"
    "  `verb` varchar(255),"
    "  `adjective` varchar(255),"
    "  `adverb` varchar(255),"
    "  PRIMARY KEY (`id`),"
    "  CONSTRAINT `tweet_analysis_ibfk_1` FOREIGN KEY (`tweet_id`) "
    "     REFERENCES `valentine_tweet` (`id`) ON DELETE CASCADE"
    ") ENGINE=InnoDB")

config = {
    'user': os.getenv("MYSQL_USER"),
    'password': os.getenv("MYSQL_PASSWORD"),
    'host': 'db',
    'port': '3306',
    'database': os.getenv("MYSQL_DATABASE"),
    'charset': 'utf8mb4'
}

cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()


def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8mb4'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)


try:
    cursor.execute("USE {}".format(DB_NAME))
except mysql.connector.Error as err:
    print("Database {} does not exists.".format(DB_NAME))
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        print("Database {} created successfully.".format(DB_NAME))
        cnx.database = DB_NAME
    else:
        print(err)
        exit(1)


for table_name in TABLES:
    table_description = TABLES[table_name]
    try:
        print("Creating table {}: ".format(table_name))
        cursor.execute(table_description)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")


cursor.close()
cnx.close()
