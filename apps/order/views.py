from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order
from .serializers import OrderSerializer
from apps.account.permissions import IsActive


class OrderCreateApiView(APIView):
    permission_classes = IsActive,

    def get(self, request):
        user = request.user
        order = Order.objects.filter(user=user)
        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        order = request.data
        serializer = OrderSerializer(data=order)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=201)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)



