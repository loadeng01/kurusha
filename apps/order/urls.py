from django.urls import path
from .views import OrderCreateApiView, OrderConfirmView

urlpatterns = [
    path('', OrderCreateApiView.as_view()),
    path('confirm/<int:pk>/', OrderConfirmView.as_view())
]
