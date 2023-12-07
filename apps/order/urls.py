from django.urls import path
from .views import OrderCreateApiView, GetInProcessOrderView

urlpatterns = [
    path('', OrderCreateApiView.as_view()),
    path('orders/', GetInProcessOrderView.as_view())
]


