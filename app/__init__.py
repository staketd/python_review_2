import telebot
from collections import defaultdict
from config import TOKEN
import sqlite3
import os
from urllib.parse import urlparse
import psycopg2
from contextlib import contextmanager

url = urlparse(os.environ['DATABASE_URL'])
dbname = url.path[1:]
user = url.username
passowrd = url.password
host = url.hostname
port = url.port


@contextmanager
def connect():
    connection = psycopg2.connect(dbname=dbname, user=user, passowrd=passowrd,
                                  host=host, port=port)
    yield connection
    connection.close()


with connect() as conn:
    cursor = conn.cursor()
    cursor.execute('''
                    create table if not exists winners(
                        username varchar(200),
                        chat_id varchar(50),
                        dt date,
                        primary key (username, chat_id)
                    );
                    ''')
    cursor.execute('''
                    create table if not exists registered(
                      username varchar(200),
                      chat_id varchar(50),
                      primary key (username, chat_id) 
                    );
                    ''')
    cursor.execute('''
                    create table if not exists last_play(
                      chat_id varchar(50) primary key,
                      dt date 
                    );
                    ''')
    conn.commit()

EVENTS = defaultdict(dict)
WEATHER_API_KEY = '6a1eaa0e205d9707ac2606ac7e191a47'
bot = telebot.TeleBot(TOKEN, threaded=True)

from app import handlers
