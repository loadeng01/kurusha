import requests
import telebot
from decouple import config
from django.http import Http404
from django.shortcuts import get_object_or_404
from geopy import GoogleV3
from apps.order.models import Order
from apps.tg.models import update_feedback
from telebot import types

TOKEN = config('TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def message_send(message):
    bot.reply_to(message, "Добро пожаловать в нашу курьерскую службу доставки! 🚚💨 Ниже будет ссылка на группу,"
                          "там вы можете отслеживать свои доставки и получать важные обновления. Начнем вместе"
                          "сделаем доставку быстрой и удобной! 📦💼")


@bot.message_handler(commands=['help'])
def message_send(message):
    help_text = (
        "Это бот курьерской службы доставки. Используйте следующие команды:\n"
        "/start - Начать взаимодействие с ботом.\n"
        "/help - Получить этот текст справки.\n"
        "/orders - Просмотреть доступные заказы.\n"
        "/contact - Связаться с поддержкой или администрацией.\n"
        "/feedback - Оставить отзыв или обратную связь."
    )

    bot.reply_to(message, help_text)


@bot.message_handler(commands=['contact'])
def message_send(message):
    contact_text = (
        "Свяжитесь с нами для поддержки или вопросов:\n"
        "Телефон: +996552590770\n"
        "Telegram: @trueBella"
    )
    bot.reply_to(message, contact_text)


user_states = {}


@bot.message_handler(commands=['feedback'])
def start_feedback(message):
    # Устанавливаем состояние "waiting_for_feedback"
    user_states[message.chat.id] = "waiting_for_feedback"

    # Отправляем сообщение с инструкциями
    bot.reply_to(message, "Оставьте свой отзыв или комментарий!")


# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "waiting_for_feedback")
def handle_feedback(message):
    user_id = int(message.from_user.id)
    user_feedback = message.text

    # Сохраняем отзыв в базе данных
    update_feedback(user_id, user_feedback)

    # Сбрасываем состояние
    user_states[message.chat.id] = None

    # Отправляем благодарственное сообщение
    bot.reply_to(message, "Спасибо за ваш отзыв! Ваше мнение очень важно для нас.")


global orders
global order_list


@bot.message_handler(commands=['orders'])
def message_send(message):
    api_url = 'http://16.170.221.153/api/order/orders/'
    response = requests.get(api_url)
    if response.status_code == 200:

        orders = response.json()
        if orders:
            order_list = []
            for order in orders:
                order_list.append([order['user'], order['address']])
                formatted_order = f'Пользователь: {order_list[-1][0]}, Адрес: {order_list[-1][1]}'
                markup = types.InlineKeyboardMarkup(row_width=1)
                button_data = f'order_{order["id"]}'
                print(f"Button Data: {button_data}")
                button = types.InlineKeyboardButton("take", callback_data=f'{order["id"]}')
                markup.add(button)
                bot.send_message(message.chat.id, f'Активные заказы:\n{formatted_order}', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'Нет активных заказов.')
    else:
        bot.send_message(message.chat.id, 'Ошибка при получении заказов. Попробуйте позже.')


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    try:
        order_id = call.data
        queryset = Order.objects.get(id=order_id)
        queryset.status = 'completed'
        queryset.save()
        bot.send_message(call.message.chat.id, f"Заказ {order_id} взят и обновлен!\n")
        coordinates = geopy(queryset.address)
        latitude, longitude = coordinates
        maps_link = generate_google_maps_link(latitude, longitude)
        bot.send_message(call.message.chat.id, f"Ссылка на Google Maps: {maps_link}")
        bot.send_message(call.message.chat.id, f"Связь с покупателем: {queryset.user}")

    except Http404:
        bot.send_message(call.message.chat.id, f"Заказ {order_id} не найден!\n")


def geopy(place):
    location = GoogleV3(api_key=config("API_GOOGLE_KEY"), domain="maps.google.ru").geocode(place)
    return location.latitude, location.longitude


def generate_google_maps_link(latitude, longitude):
    google_maps_link = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
    return google_maps_link
