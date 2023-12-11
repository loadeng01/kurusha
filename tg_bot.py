import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.tg.telegram.commands.tg import bot

bot.infinity_polling()
