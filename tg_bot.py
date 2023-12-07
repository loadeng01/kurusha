import os

import django
from apps.tg.telegram.commands.tg import bot

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


bot.infinity_polling()
