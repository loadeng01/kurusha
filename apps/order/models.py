from django.db import models
from django.contrib.auth import get_user_model
from apps.product.models import Product

User = get_user_model()


class OrderItem(models.Model):
    order = models.ForeignKey('Order', related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f'{self.product.title} {self.order.user}'


class OrderStatus(models.TextChoices):
    opened = 'opened'
    in_process = 'in_process'
    completed = 'completed'


class Order(models.Model):
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    product = models.ManyToManyField(Product, through=OrderItem)
    address = models.CharField(max_length=150)
    total_sum = models.DecimalField(max_digits=9, decimal_places=2, blank=True)
    comment = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.opened)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id} --> {self.user}'


