import telebot
import sqlite3
import random
import json
import requests
import datetime
from app import WEATHER_API_KEY, connect


def create_event_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    roll = telebot.types.InlineKeyboardButton(text='Ролл',
                                              callback_data='roll')
    stop = telebot.types.InlineKeyboardButton(text='Остановить розыгрыш',
                                              callback_data='stop')
    markup.add(roll, stop)
    return markup


def get_text_by_event(event):
    text = '*Результаты розыгрыша!*\n'
    maxvalue = max(event['results'])
    winners = []
    for i in zip(event['participants'], event['results']):
        if i[1] == maxvalue:
            winners.append(i)
        else:
            text += '{}: `{}`\n'.format(i[0], i[1])
    text += '\n*Победител' + ('и' if len(winners) > 1 else 'ь') + '!*\n'
    for i in winners:
        text += '{}: `{}`\n'.format(i[0], i[1])
    return text


def parse_args(text):
    return text.split()[1:]


def get_weather_data(city):
    url = 'http://api.openweathermap.org/data/2.5/weather'
    payload = {"q": city, "APPID": WEATHER_API_KEY, "units": "metric",
               'lang': 'ru'}
    res = requests.get(url, payload)
    return json.loads(res.text)


def get_wind_direction(deg):
    dirs_deg = [22.5]
    for i in range(7):
        dirs_deg.append(dirs_deg[-1] + 45)
    dirs = ['СВ', 'В', 'ЮВ', 'Ю', 'ЮЗ', 'З', 'СЗ']
    for i in range(7):
        if dirs_deg[i] <= deg <= dirs_deg[i + 1]:
            return dirs[i]
    return 'C'


def get_pressur_mm(hpa):
    return round(hpa / 133.322)


def get_winners_this_year(chat_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('''select username, count(dt)
                            from winners
                            where chat_id = '{}' and 
                            strftime('%Y', 'now') == strftime('%Y', dt)
                            group by username
                            order by count(dt)'''.format(chat_id))
        return cursor.fetchmany(10)


def get_winners_text(arr):
    text = 'Топ-10 участников за этот год!\n'
    for place, user in enumerate(arr):
        text += '*{}.* {} - _{}_ _раз(а)_\n'.format(place + 1, user[0], user[1])
    return text


def register_user(chat_id, username):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('''select * from registered
                          where username = '{}' and chat_id = '{}' '''.format(
            username, chat_id))
        if cursor.fetchone() is not None:
            return False
        cursor.execute('''insert into registered
                        values('{}', '{}')  
                        '''.format(username, chat_id))
        conn.commit()
        return True


def is_possible(chat_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('''select * from last_play
                            where chat_id = '{}' and dt = current_date'''.format(
            chat_id))

        if cursor.fetchone() is not None:
            return 1
        cursor.execute('''select * from registered
                            where chat_id = '{}' '''.format(chat_id))
        if cursor.fetchone() is None:
            return 2
        return 0


def choose_winner(chat_id):
    with sqlite3.connect() as conn:
        cursor = conn.cursor()
        cursor.execute('''select username from registered
                            where chat_id = '{}' '''.format(chat_id))
        winner_username = random.choice(cursor.fetchall())[0]
        cursor.execute('''insert into winners 
                            values ('{}', '{}', date())'''.format(
            winner_username,
            chat_id))
        cursor.execute('''insert into last_play
                            values ('{0}', current_date)
                            on conflict(chat_id) do update last_play 
                            set dt = current_date
                            where chat_id = '{0}' '''.format(chat_id))
        conn.commit()
        return winner_username
