from django.contrib import admin
from .models import TelegramUser



@admin.register(TelegramUser)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username')
