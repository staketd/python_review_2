from app import bot, EVENTS, PIZZA
from app import data_base
import app.support_funtions as sf
import random


@bot.message_handler(commands=['help'])
def handle_help(message):
    text = '/roll - случайный выбор числа от 1 до 100\n'
    text += '/flip - бросок монетки\n'
    text += '/event - Розыгрыш\n'
    text += '/weather_in_city - погода в городе(город указывать на английском)\n'
    text += '/register - зарегистрироваться на ежедневый розыгрыш\n'
    text += '/play - Начать ежедневный розыгрыш\n'
    text += '/winners - топ 10 победителей за текущий год\n'
    bot.reply_to(message, text)


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id,
                     'Привет! Я бот, который будет помогать'
                     ' тебе решить, кто победил в споре')


@bot.message_handler(commands=['weather_in_city'])
def handle_weather(message):
    args = sf.parse_args(message.text)
    if len(args) == 0:
        bot.reply_to(message, 'Нужно указать имя города!')
        return
    city = args[0]
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
            sf.get_wind_direction(res['wind'].get('deg', 0)))
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


@bot.message_handler(commands=['register'])
def handle_register(message):
    result = data_base.register_user(str(message.chat.id),
                                     message.from_user.username)
    if result:
        bot.reply_to(message, 'Ты зарегестрирован(а) на ежедневную лоттерею!')
    else:
        bot.reply_to(message, 'Ты уже зарегистрирован(а)!')


@bot.message_handler(commands=['winners'])
def handle_winners(message):
    text = sf.get_winners_text(
        data_base.get_winners_this_year(str(message.chat.id)))
    bot.reply_to(message, text, parse_mode='Markdown')


@bot.message_handler(commands=['pizza'])
def handle_pizza(message):
    pizza = PIZZA[message.chat.id]
    if pizza.get('running', False):
        bot.reply_to(message,
                     'Вы еще не выбрали того кто пойдет за пиццой в прошлый '
                     'раз! Либо выберете, либо {} должен нажать стоп.'.format(
                         pizza['creator_username']))
    else:
        pizza['running'] = True
        pizza['creator_username'] = message.from_user.username
        pizza['participants'] = []
        pizza['result'] = []
        bot.reply_to(message, text='Да начнется выбор пиценосца!',
                     reply_markup=sf.create_pizza_markup())


@bot.message_handler(commands=['play'])
def handle_play(message):
    res = data_base.is_possible(str(message.chat.id))
    if res == 1:
        bot.reply_to(message, 'Сегодня уже проводился розыгрыш!')
    elif res == 2:
        bot.reply_to(message, 'Никто не зарегистрирован!')
    else:
        winner = data_base.choose_winner(str(message.chat.id))
        bot.reply_to(message,
                     'Сегодняшним победителем становится @{}!!'.format(winner))


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
    pizza = PIZZA[call.message.chat.id]
    if call.data == 'roll_event':
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

    if call.data == 'participate_pizza':
        if not pizza.get('running', False):
            bot.answer_callback_query(call.id, 'Выбор лоха еще не начат', True)
        elif call.from_user.username in pizza['participants']:
            bot.answer_callback_query(call.id, 'Ты уже кандидат!', True)
        else:
            pizza['participants'].append(call.from_user.username)
            text = sf.get_text_by_pizza(pizza)
            bot.edit_message_text(text, call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=sf.create_pizza_markup(),
                                  parse_mode='Markdown')
            bot.answer_callback_query(call.id, 'Ты стал кандидатом в лохи!')

    if call.data == 'choose_pizza':
        if not pizza.get('running', False):
            bot.answer_callback_query(call.id, 'Выбор лоха еще не начат!',
                                      True)
        elif call.from_user.username != pizza['creator_username']:
            bot.answer_callback_query(call.id,
                                      'Только {} может выбрать лоха!'.format(
                                          pizza['creator_username']), True)
        elif len(pizza['participants']) == 0:
            bot.answer_callback_query(call.id,
                                      'Вы совсем дебилы?! Не из кого выбирать!',
                                      True)
        else:
            text = sf.get_text_by_pizza(pizza)
            pizza['running'] = False
            text += '\n*Выбор завершился!*'
            bot.edit_message_text(text, call.message.chat.id,
                                  call.message.message_id,
                                  parse_mode='Markdown')
            bot.send_message(call.message.chat.id,
                             'И лохом становится .... {}!'.format(
                                 random.choice(pizza['participants'])))

    if call.data == 'stop_event':
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


@bot.message_handler(commands=['clean'])
def clean(message):
    if message.from_user.username == 'Stakett':
        data_base.clean()
    else:
        bot.reply_to(message, 'У вас нет прав на эту комманду!')
