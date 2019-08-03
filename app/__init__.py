import telebot
from collections import defaultdict
from config import TOKEN
from app.db import DataBase

EVENTS = defaultdict(dict)
PIZZA = defaultdict(dict)
WEATHER_API_KEY = '6a1eaa0e205d9707ac2606ac7e191a47'
data_base = DataBase('DATABASE_URL')
data_base.create_tables()
bot = telebot.TeleBot(TOKEN, threaded=True)

from app import handlers
