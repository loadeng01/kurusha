import requests
import telebot
from decouple import config
from django.http import Http404
from django.shortcuts import get_object_or_404

from apps.order.models import Order
from apps.tg.models import update_feedback
from telebot import types

TOKEN = config('TOKEN')
bot = telebot.TeleBot(TOKEN)
yandex_token = config('YANDEX_TOKEN')


def geocode(place_name):
    api_key = yandex_token
    base_url = "https://geocode-maps.yandex.ru/1.x/"

    params = {
        'apikey': api_key,
        'format': 'json',
        'geocode': place_name,
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if data['response']['GeoObjectCollection']['metaDataProperty']['GeocoderResponseMetaData']['found'] > 0:
            # Получаем координаты первого результата
            coordinates = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
            return tuple(map(float, coordinates.split()))
        else:
            return None
    except Exception as e:
        print(f"Ошибка при выполнении запроса к Яндекс.Геокодеру: {e}")
        return None


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
        bot.send_message(call.chat.id, f"Заказ {order_id} взят и обновлен!\n")
        coordinates = get_coordinates_from_place(queryset.address)

        if coordinates:
            latitude, longitude = coordinates

            # Создаем ссылку на Яндекс.Карты с указанием координат и автоматическим рассчетом маршрута
            maps_link = f"https://yandex.ru/maps/?rtext={latitude},{longitude}&rtt=auto"

            bot.send_message(call.chat.id, f"Координаты для адреса '{queryset.address}': ({latitude}, {longitude})\n"
                                           f"Ссылка на Яндекс.Карты: {maps_link}")
        else:
            bot.send_message(call.chat.id, f"Координаты для адреса '{queryset.address}' не найдены.")
    except Http404:
        bot.send_message(call.chat.id, f"Заказ {order_id} не найден!\n")
    except Exception as e:
        print(f"Ошибка при обработке колбэка: {e}")


def get_coordinates_from_place(place_name):
    try:
        coordinates = geocode(place_name)

        if coordinates:
            latitude, longitude = coordinates
            print(f"Координаты для места '{place_name}': ({latitude}, {longitude})")

        else:
            return None
    except Exception as e:
        print(f"Ошибка при получении координат: {e}")
        return None

