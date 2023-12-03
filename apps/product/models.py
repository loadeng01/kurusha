from django.db import models
from django.contrib.auth import get_user_model
from apps.category.models import Category

User = get_user_model()


class Product(models.Model):
    title = models.CharField(max_length=100)
    price = models.IntegerField()
    description = models.TextField(blank=False, null=False)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.title


