from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from .serializers import *
from rest_framework import generics
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from .tasks import send_confirmation_email
from .permissions import IsAdminOrEmployee
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

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
        print(code)
        user = get_object_or_404(User, activation_code=code)
        user.is_active = True
        user.activation_code = ''
        user.save()
        return Response('Successfully activate', status=200)


class LoginView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny, )


class Pagination(PageNumberPagination):
    page_size = 3
    page_query_param = 'page'


# class UsersViewSet(generics.ListAPIView):
#     permission_classes = permissions.IsAdminUser,
#     queryset = User.objects.all()
#     pagination_class = Pagination
#     serializer_class = UserSerializer
#     filter_backends = (SearchFilter, DjangoFilterBackend)
#     search_fields = ('email', 'username')
#     filterset_fields = ('is_staff', 'is_superuser', 'is_active')


class UserView(APIView):
    serializer_class = AccountSerializer
    permission_classes = permissions.IsAuthenticated,

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
        instance = User.objects.get(email=self.request.user)
        serializer = self.serializer_class(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=200)

    def delete(self, request, *args, **kwargs):
        instance = User.objects.get(email=self.request.user)
        instance.delete()
        return Response(status=204)


