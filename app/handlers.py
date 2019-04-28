from app import bot, EVENTS
import telebot
import app.support_funtions as sf
import random


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id,
                     'Привет! Я бот, который будет помогать'
                     ' тебе решить, кто победил в споре')


@bot.message_handler(commands=['weather_in_city'])
def handle_weather(message):
    city = sf.parse_args(message.text)[0]
    res = sf.get_weather_data(city)
    if res['cod'] != 200:
        if res['message'] == 'city not found':
            bot.reply_to(message, 'Город с таким именем не найден')
        else:
            bot.reply_to(message, res['message'])
    else:
        text = '*Погода в городе: {}*\n'.format(
            res['weather'][0]['description'])
        text += 'Температура: {}Сº\n'.format(res['main']['temp'])
        text += 'Скорость ветра: {} м/c\n'.format(res['wind']['speed'])
        text += 'Направление ветра: {}\n'.format(
            sf.get_wind_direction(res['wind']['deg']))
        text += 'Облачность: {}%\n'.format(res['clouds']['all'])
        text += 'Влажность: {}%\n'.format(res['main']['humidity'])
        text += 'Атмосферное давление: {} мм рт ст\n'.format(
            sf.get_pressur_mm(res['main']['pressure']))
        bot.reply_to(message, text, parse_mode='Markdown')


@bot.message_handler(commands=['flip'])
def handle_flip(message):
    answer = 'Решка' if random.randint(0, 1) else 'Орел'
    bot.reply_to(message, answer)


@bot.message_handler(commands=['roll'])
def handle_roll(message):
    bot.reply_to(message, random.randint(1, 100))


@bot.message_handler(commands=['event'])
def handle_start_event(message):
    event = EVENTS[message.chat.id]
    if event.get('running', False):
        bot.reply_to(message,
                     'Розыгрыш уже начат, {} должен завершить его'.format(
                         event['creator_username']))
    else:
        event['running'] = True
        event['creator_username'] = message.from_user.username
        event['participants'] = []
        event['results'] = []
        bot.reply_to(message, text='Начало розыгрыша',
                     reply_markup=sf.create_event_markup())


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    event = EVENTS[call.message.chat.id]
    if call.data == 'roll':
        if not event.get('running', False):
            bot.answer_callback_query(call.id, 'Розыгрыш еще не начат', True)
        elif call.from_user.username in event['participants']:
            bot.answer_callback_query(call.id,
                                      'Ты уже получил свой результат!', True)
        else:
            event['participants'].append(call.from_user.username)
            result = random.randint(1, 100)
            event['results'].append(result)
            text = sf.get_text_by_event(event)
            bot.edit_message_text(text, call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=sf.create_event_markup(),
                                  parse_mode='Markdown')
            bot.answer_callback_query(call.id,
                                      'Ты выбросил {}!'.format(result), True)
    if call.data == 'stop':
        if not event.get('running', False):
            bot.answer_callback_query(call.id, 'Розыгрыш еще не начат', True)
        elif call.from_user.username != event['creator_username']:
            bot.answer_callback_query(call.id,
                                      'Только {} может завершить розыгрыш!'.format(
                                          event['creator_username']), True)
        elif len(event['participants']) == 0:
            bot.answer_callback_query(call.id,
                                      'Никто не участвовал в розыгрыше!', True)
        else:
            text = sf.get_text_by_event(event)
            event['running'] = False
            text += '\n*Розыгрыш окончен!*'
            bot.edit_message_text(text, call.message.chat.id,
                                  call.message.message_id,
                                  parse_mode='Markdown')
