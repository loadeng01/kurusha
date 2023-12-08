from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework import permissions
from .serializers import *
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from .tasks import send_confirmation_email, reset_password_email
from .permissions import IsActive
from django.shortcuts import render
from django.contrib.auth.hashers import check_password

User = get_user_model()


class RegistrationCustomerView(APIView):
    permission_classes = permissions.AllowAny,

    def post(self, request):
        serializer = RegisterCustomerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user:
            try:
                send_confirmation_email.delay(user.email, user.activation_code)
            except:
                return Response({'message': 'Registered, but trouble with email',
                                 'data': serializer.data}, status=201)
        return Response(serializer.data, status=201)


class RegisterCourierView(APIView):
    permission_classes = permissions.AllowAny,

    def post(self, request):
        serializer = RegisterCustomerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user:
            try:
                send_confirmation_email.delay(user.email, user.activation_code)
            except:
                return Response({'message': 'Registered, but trouble with email',
                                 'data': serializer.data}, status=201)
        return Response(serializer.data, status=201)


class ActivationEmailView(APIView):
    def get(self, request):
        code = request.GET.get('u')
        user = get_object_or_404(User, activation_code=code)
        user.is_active = True
        user.activation_code = ''
        user.save()
        return render(request, 'whistle.html')
        # return Response('Successfully activate', status=200)


class LoginView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny, )


class Pagination(PageNumberPagination):
    page_size = 3
    page_query_param = 'page'


class UserView(APIView):
    serializer_class = AccountSerializer
    permission_classes = IsActive,

    def get_queryset(self):
        return User.objects.get(email=self.request.user)

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = User.objects.get(email=self.request.user)
        serializer = self.serializer_class(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=200)

    def patch(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)

        if request.data.get('email'):
            return Response('Нельзя менять Email', status=400)

        instance = User.objects.get(email=self.request.user)
        serializer = self.serializer_class(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=200)

    def delete(self, request, *args, **kwargs):
        try:
            user_instance = self.request.user
            instance = User.objects.get(email=user_instance)
            old_password = request.data.get('password')
        except:
            return Response('error', status=400)

        if not check_password(old_password, user_instance.password):
            return Response('Неверный пароль', status=400)

        instance.delete()
        return Response('Successfully deleted', status=204)


class ChangePasswordView(APIView):
    permission_classes = IsActive,

    def post(self, request, *args, **kwargs):
        user_instance = self.request.user
        old_password = request.data.get('password')
        new_password = request.data.get('new_password')
        password_confirm = request.data.get('password_confirm')

        if not check_password(old_password, user_instance.password):
            return Response('Старый пароль неверный', status=400)

        if new_password != password_confirm:
            return Response('Новые пароли не совпадают', status=400)

        user_instance.set_password(new_password)
        user_instance.save()

        return Response('Successfully changed', status=200)


class ResetPasswordView(APIView):
    permission_classes = IsActive,

    def post(self, request, *args, **kwargs):
        user_instance = self.request.user
        password = request.data.get('password')
        password_confirm = request.data.get('password_confirm')

        if password != password_confirm:
            return Response('Новые пароли не совпадают', status=400)

        user_instance.set_password(password)
        user_instance.save()

        return Response('Successfully changed', status=200)


class SendEmailView(APIView):
    permission_classes = IsActive,

    def post(self, request):
        instance = User.objects.get(email=self.request.user)
        serializer = AccountSerializer(instance)
        user = serializer.data.get('email')
        reset_password_email.delay(user)

        return Response('Successfully send', status=200)





