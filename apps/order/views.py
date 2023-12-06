from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order
from .serializers import OrderSerializer
from apps.account.permissions import IsActive


# class OrderCreateApiView(ListCreateAPIView):
#     serializer_class = OrderSerializer
#     permission_classes = IsActive,
#
#     def create(self, request, *args, **kwargs):
#         user = request.user
#         orders = user.orders.all()
#         serializer = self.serializer_class(instance=orders, many=True)
#         return Response(serializer.data, status=200)
#
#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)


class OrderCreateApiView(APIView):
    permission_classes = IsActive,

    def get(self, request):
        user = request.user
        order = Order.objects.filter(user=user)
        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        order = request.data
        print(request.data, '1111111111111111111111')
        serializer = OrderSerializer(data=order)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderConfirmView(APIView):
    def get(self, request, pk):
        order = Order.objects.get(pk=pk)
        order.status = 'completed'
        order.save()
        return Response({'message': 'Вы подтвердили'}, status=200)




