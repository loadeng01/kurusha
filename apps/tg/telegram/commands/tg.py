import requests
import telebot
from decouple import config
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


@bot.message_handler(commands=['orders'])
def message_send(message):
    api_url = 'http://16.170.221.153/api/order/orders/'
    response = requests.get(api_url)
    global order_list
    order_list = []
    if response.status_code == 200:
        orders = response.json()
        if orders:
            for order in orders:
                order_list.append([order['user'], order['address']])
                formatted_order = f'Пользователь: {order_list[-1][0]}, Адрес: {order_list[-1][1]}'
                markup = types.InlineKeyboardMarkup(row_width=1)
                button = types.InlineKeyboardButton("ВЗЯТЬ", callback_data=f'take_order_{order["id"]}')
                markup.add(button)
                bot.send_message(message.chat.id, f'Активные заказы:\n{formatted_order}', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'Нет активных заказов.')
    else:
        bot.send_message(message.chat.id, 'Ошибка при получении заказов. Попробуйте позже.')


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('take_order_'))
def take_order_callback(callback):
    order_id = callback.data.split('_')[2]
    order_taken_message = f'Заказ {order_id} взят!'
    bot.send_message(callback.message.chat.id, order_taken_message)


# try:
    #     order_id = callback.data.split('_')[1]
    #     order_info = find_order_info_by_id(order_id)
    #     if order_info:
    #         bot.send_message(callback.message.chat.id, f"Заказ {order_id} взят!\n{order_info}")
    #     else:
    #         bot.send_message(callback.message.chat.id, "Ошибка: заказ не найден.")
    # except Exception as e:
    #     print(f"Ошибка при обработке колбэка: {e}")


def find_order_info_by_id(order_id):
    for order_info in order_list:
        if str(order_id) in order_info:
            return order_info
    return None