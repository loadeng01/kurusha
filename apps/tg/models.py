from django.db import models


class TelegramUser(models.Model):
    user_id = models.BigIntegerField()
    username = models.CharField(max_length=255, blank=True, null=True)
    feedback_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} - {self.created_at}"


def update_feedback(user_id, new_feedback_text):
    # Получаем существующий отзыв
    existing_user = TelegramUser.objects.filter(user_id=user_id).first()

    if existing_user:
        # Если отзыв существует, обновляем его, добавляя новый текст
        existing_user.feedback_text += f"\n{new_feedback_text}"
        existing_user.save()
        print("Отзыв был успешно обновлен.")
    else:
        # Если отзыва нет, создаем новый
        TelegramUser.objects.create(user_id=user_id, feedback_text=new_feedback_text)
        print("Новый отзыв был создан.")