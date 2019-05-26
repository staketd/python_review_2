import telebot
import json
import requests
from app import WEATHER_API_KEY


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
    side_degrees = 45
    start_degree = 22.5
    dirs_deg = [start_degree]
    for i in range(7):
        dirs_deg.append(dirs_deg[-1] + side_degrees)
    dirs = ['СВ', 'В', 'ЮВ', 'Ю', 'ЮЗ', 'З', 'СЗ']
    for i in range(7):
        if dirs_deg[i] <= deg <= dirs_deg[i + 1]:
            return dirs[i]
    return 'C'


def get_pressur_mm(hpa):
    return round(hpa / 133.322)


def get_winners_text(arr):
    text = 'Топ-10 участников за этот год!\n'
    for place, user in enumerate(arr):
        name = user[0].replace("_", "")
        text += '*{}.* _{}_ - _{}_ _раз(а)_\n'.format(place + 1, name,
                                                    user[1])
    return text
