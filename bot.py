from dotenv import load_dotenv
import os
import telegram
from telegram import Update
from telegram.ext import Filters
from telegram.ext import CallbackContext
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup
from telegram import KeyboardButton
import json
import logging
from datetime import datetime, timedelta
#import telegramcalendar
import random

states_database = {}

def create_test_game(context):
    context.user_data['creator_telephone_number'] = '+79528949027'
    context.user_data['creator_first_name'] = 'Евгений'
    context.user_data['creator_username'] = 'OxFFFFFFF'
    context.user_data['game_name'] = 'Тайный Санта'
    context.user_data['cost_limit'] = '500-1000 рублей'
    context.user_data['registration_period'] = '31.12.2021'
    context.user_data['departure_date'] = '15.01.2022'
    context.user_data['game_id'] = 123456

def chunks_generators(buttons, chunks_number):
    for button in range(0, len(buttons), chunks_number):
        yield buttons[button : button + chunks_number]


def keyboard_maker(buttons, number):
    keyboard = list(chunks_generators(buttons, number))
    markup = ReplyKeyboardMarkup(
        keyboard, resize_keyboard=True, one_time_keyboard=True
    )
    return markup


def start(update, context):
    create_test_game(context)
    game_id = update.message.text[7:]
    if game_id:
        context.user_data['game_id'] = game_id
    chat_id = update.effective_message.chat_id

    buttons = ['Создать игру', 'Вступить в игру']
    markup = keyboard_maker(buttons, 2)
    context.bot.send_message(
        chat_id=chat_id,
        text=' Организуй или присоединись к тайному обмену подарками,'
             ' запусти праздничное настроение!',
        reply_markup=markup,
    )

    return 'SELECT_BRANCH'

def select_branch(update, context):
    user = update.message.from_user
    chat_id = update.effective_message.chat_id
    user_message = update.message.text
    if user_message == 'Создать игру':
        reply_markup = telegram.ReplyKeyboardMarkup([[telegram.KeyboardButton(
            'Поделиться номером телефона',
            request_contact=True,
        )]])

        context.bot.send_message(
            chat_id=chat_id,
            text='Введи свой номер телефона или нажми кнопку',
            reply_markup=reply_markup,
        )
        return 'GET_CONTACT'

    if user_message == 'Вступить в игру':
        context.bot.send_message(
            chat_id=chat_id,
            text='Введите 6-значный идентификатор игры',
        )
        return 'CHECK_GAME'

def get_player_name(update, context):
    user = update.message.from_user
    chat_id = update.effective_message.chat_id
    user_message = update.message.text
    context.user_data['player_name'] = user_message

    buttons = ['Завершить']
    markup = keyboard_maker(buttons, 1)
    context.bot.send_message(
        chat_id=chat_id,
        text=' Введи свой виш-лист по одной вещи\n'
             'Когда закончишь - нажми кнопку',
        reply_markup=markup,
    )
    context.user_data['wish_list'] = []
    return 'GET_WISH_LIST'


def get_wish_list(update, context):
    user = update.message.from_user
    chat_id = update.effective_message.chat_id
    user_message = update.message.text
    if user_message == 'Завершить':
        pass
    context.user_data['wish_list'].append(user_message)
    print(context.user_data['wish_list'])

def check_game(update, context):
    user = update.message.from_user
    chat_id = update.effective_message.chat_id
    user_message = update.message.text
    print(user_message, type(user_message))
    print(context.user_data.get('game_id'), type(context.user_data.get('game_id')))
    print(context.user_data)
    if int(user_message) == context.user_data.get('game_id'):
        context.bot.send_message(
            chat_id=chat_id,
            text=' Какое будет твоё имя в игре?',
        )
        return 'GET_PLAYER_NAME'
    else:
        buttons = ['Создать игру', 'Вступить в игру']
        markup = keyboard_maker(buttons, 2)
        context.bot.send_message(
            chat_id=chat_id,
            text='Игры с таким идентификатором не существует',
            reply_markup=markup,
        )
        return 'SELECT_BRANCH'


def show_game_info(update, context):
    user = update.message.from_user
    chat_id = update.effective_message.chat_id
    user_message = update.message.text
    context.bot.send_message(
        chat_id=chat_id,
        text=f'Название игры: {context.user_data["game_name"]}\n'
             f'Ограничение стоимости: {context.user_data["cost_limit"]}\n'
             f'Период регистрации до: {context.user_data["registration_period"]}\n'
             f'Дата отправки подарков: {context.user_data["departure_date"]}'
    )


def get_contact(update, context):
    user = update.message.from_user
    user_input = update.effective_message.text
    chat_id = update.effective_message.chat_id
    if update.message.contact is not None:
        user_phone_number = update.message.contact.phone_number
        context.user_data['creator_telephone_number'] = user_phone_number
    else:
        user_phone_number = update.message.text
        context.user_data['creator_telephone_number'] = user_phone_number

    context.user_data['creator_first_name'] = user.first_name
    context.user_data['creator_username'] = user.username
    context.bot.send_message(
        chat_id=chat_id,
        text='Введите название игры',
        reply_markup=telegram.ReplyKeyboardRemove()
    )

    return 'GET_GAME_NAME'


# def telephone_number_handler(update, context):
#     user_input = update.effective_message.text
#     chat_id = update.effective_message.chat_id
#     if update.message.contact is not None:
#         user_phone_number = update.message.contact.phone_number
#         context.user_data['creator_telephone_number'] = user_phone_number
#     else:
#         user_phone_number = update.message.text
#         context.user_data['creator_telephone_number'] = user_phone_number
#     buttons = ['Подтвердить', 'Ввести другой']
#     markup = keyboard_maker(buttons, 1)
#     context.bot.send_message(
#         chat_id=chat_id,
#         text=f'Ваш номер {user_phone_number}?',
#         reply_markup=markup,
#     )
#
#     return 'CREATE_GAME'


def create_game(update, context):
    chat_id = update.effective_message.chat_id
    user_message = update.message.text

    return 'GET_GAME_NAME'


def get_game_name(update, context):
    chat_id = update.effective_message.chat_id
    user_message = update.message.text

    context.user_data['game_name'] = user_message
    buttons = ['До 500 рублей',
               '500-1000 рублей',
               '1000-2000 рублей',
    ]
    markup = keyboard_maker(buttons, 3)
    context.bot.send_message(
        chat_id=chat_id,
        text='Введите ограничение стоимости подарка'
             'или нажмите одну из кнопок',
        reply_markup=markup,
    )
    return 'GET_COST_LIMIT'

def get_cost_limit(update, context):
    chat_id = update.effective_message.chat_id
    user_message = update.message.text
    context.user_data['cost_limit'] = user_message
    buttons = ['25.12.2021', '31.12.2021']
    markup = keyboard_maker(buttons, 2)
    context.bot.send_message(
        chat_id=chat_id,
        text='Введите дату окончания регистрации участников'
             ' (до 12.00 МСК) или нажмите одну из кнопок',
        reply_markup=markup,
    )
    return 'GET_REGISTRATION_PERIOD'


def get_registration_period(update, context):
    chat_id = update.effective_message.chat_id
    user_message = update.message.text
    context.user_data['registration_period'] = user_message

    # здесь будет формирование календаря
    context.bot.send_message(
        chat_id=chat_id,
        text='Дата отправки подарка?',
        #reply_markup=calendar,
    )

    return 'GET_DEPARTURE_DATE'


def get_departure_date(update, context):
    chat_id = update.effective_message.chat_id
    user_message = update.message.text
    context.user_data['departure_date'] = user_message
    buttons = ['Получить ссылку для регистрации']
    markup = keyboard_maker(buttons, 1)
    context.bot.send_message(
        chat_id=chat_id,
        text='Отлично, Тайный Санта уже готовится к раздаче подарков!',
        reply_markup=markup
    )
    return 'CREATE_REGISTRATION_LINK'


def create_registration_link(update, context):
    chat_id = update.effective_message.chat_id
    user_message = update.message.text
    game_id = random.randint(111111, 999999)
    registration_link = f'https://t.me/secret_santa_devman_bot?start={game_id}'

    buttons = ['Создать игру', 'Вступить в игру']
    markup = keyboard_maker(buttons, 2)
    context.bot.send_message(
        chat_id=chat_id,
        text='Вот ссылка для приглашения участников игры, по которой '
             f'они смогут зарегистрироваться: {registration_link}',
        reply_markup=markup,
    )
    context.user_data['game_id'] = game_id
    print(context.user_data)

    return 'SELECT_BRANCH'


def handle_user_reply(update: Update, context: CallbackContext):
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
        user_id = update.message.from_user.id

    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply and '/start' in user_reply:
        user_state = 'START'

    else:
        user_state = states_database.get(chat_id)
    states_functions = {
        'START': start,
        'CREATE_GAME': create_game,
        #'TELEPHONE_NUMBER_HANDLER': telephone_number_handler,
        'GET_CONTACT': get_contact,
        'GET_GAME_NAME': get_game_name,
        'GET_COST_LIMIT': get_cost_limit,
        'GET_REGISTRATION_PERIOD': get_registration_period,
        'GET_DEPARTURE_DATE': get_departure_date,
        'CREATE_REGISTRATION_LINK': create_registration_link,
        'SELECT_BRANCH': select_branch,
        'CHECK_GAME': check_game,
        'GET_PLAYER_NAME': get_player_name,
        'GET_WISH_LIST': get_wish_list,
    }

    state_handler = states_functions[user_state]
    next_state = state_handler(update, context)
    states_database.update({chat_id: next_state})


def main():
    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', handle_user_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_user_reply))
    dispatcher.add_handler(MessageHandler(Filters.contact, handle_user_reply))
    #dispatcher.add_handler(MessageHandler(Filters.location, handle_user_reply))
    dispatcher.add_handler(CallbackQueryHandler(handle_user_reply))
    updater.start_polling()


if __name__ == '__main__':
    main()
