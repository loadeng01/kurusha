from django.db import models
from apps.product.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()


class Favorite(models.Model):
    owner = models.ForeignKey(User, related_name='favorites', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='favorites', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('owner', 'product')
