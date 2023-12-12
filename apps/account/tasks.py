from django.core.mail import send_mail
from django.utils.html import format_html
# from celery import shared_task
from config.celery import app


@app.task()
def send_confirmation_email(email, code):
    activation_url = f'http://16.170.221.153/api/account/activate/?u={code}'

    message = format_html(
        '<h2>Hello, activate your account!</h2>\n'
        'Click on the word to activate'
        "<br><a href={}>{}</a></br>"
        "<p>Don't show it anyone</p>",
        activation_url,
        'CLICK HERE'
    )

    send_mail(
        'Hello, activate your account!',
        '',
        'checkemail@gmail.com',
        [email],
        fail_silently=False,
        html_message=message
    )


@app.task()
def reset_password_email(email):
    url = 'http://16.170.221.153/api/your_account/change_password/'

    message = format_html(
        '<h2>Hello, reset your password!</h2>\n'
        'Click on the word to change'
        "<br><a href={}>{}</a></br>"
        "<p>Don't show it anyone</p>",
        url,
        'CHANGE'
    )

    send_mail(
        'Reset Password!',
        '',
        'checkemail@gmail.com',
        [email],
        fail_silently=False,
        html_message=message
    )


@app.task()
def send_tg_bot(email):
    url = 'https://t.me/test123esf_bot'

    message = format_html(
        '<h2>Привет, добро пожаловать в нашу команду</h2>\n'
        'Вот ссылка на телеграм бота с которым ты будешь работать'
        "<br><a href={}>{}</a></br>"
        "<p>Don't show it anyone</p>",
        url,
        'БОТ'
    )

    send_mail(
        'Добро пожаловать в команду',
        '',
        'checkemail@gmail.com',
        [email],
        fail_silently=False,
        html_message=message
    )


