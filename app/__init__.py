import telebot
from collections import defaultdict
from config import TOKEN
import sqlite3

conn = sqlite3.connect('database.db')
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
conn.close()

EVENTS = defaultdict(dict)
WEATHER_API_KEY = '6a1eaa0e205d9707ac2606ac7e191a47'
bot = telebot.TeleBot(TOKEN, threaded=True)

from app import handlers




