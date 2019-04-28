import telebot
from collections import defaultdict

bot = None

EVENTS = defaultdict(dict)
WEATHER_API_KEY = '6a1eaa0e205d9707ac2606ac7e191a47'


def init_bot(token):
    global bot
    bot = telebot.TeleBot(token)
    from app import handlers
