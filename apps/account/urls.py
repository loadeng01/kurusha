from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('register/', views.RegistrationCustomerView.as_view()),
    path('register_courier/', views.RegisterCourierView.as_view()),
    path('activate/', views.ActivationEmailView.as_view()),
    path('your_account/', views.UserView.as_view()),
    path('your_account/change_password/', views.ResetPasswordView.as_view()),
    path('send/', views.SendEmailView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
]
