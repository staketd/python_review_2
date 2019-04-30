import flask
import os
from telebot import types
from config import TOKEN
from app import bot

# server = flask.Flask(__name__)
#
#
# @server.route('/' + TOKEN, methods=['POST'])
# def get_message():
#     bot.process_new_updates(
#         [types.Update.de_json(flask.request.stream.read().decode('utf-8'))])
#     return '!', 200
#
#
# @server.route('/')
# def webhook():
#     bot.remove_webhook()
#     bot.set_webhook(url='https://python-review-2.herokuapp.com/' + TOKEN)
#     return '!', 200
#
#
# if __name__ == '__main__':
#     server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

import app
app.bot.remove_webhook()
app.bot.polling()
