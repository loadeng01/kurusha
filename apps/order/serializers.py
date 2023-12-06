from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_title = serializers.ReadOnlyField(source='product.title')

    class Meta:
        model = OrderItem
        fields = ('product', 'product_title', 'quantity')


class OrderSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    user = serializers.CharField(source='user.full_name')
    products = OrderItemSerializer(write_only=True, many=True)

    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        products = validated_data.pop('products')
        total_sum = 0

        for product in products:
            try:
                total_sum += product['quantity'] * product['product'].price
            except:
                total_sum += product['product'].price

        order = Order.objects.create(status='in_process', total_sum=total_sum, **validated_data)

        for product in products:
            try:
                OrderItem.objects.create(order=order, product=product['product'], quantity=product['quantity'])
            except:
                OrderItem.objects.create(order=order, product=product['product'])

        return order

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['product'] = OrderItemSerializer(instance.items.all(), many=True).data
        print(repr['user'], '1111111111111111111')
        # repr['user_phone_number'] = self.user.phone_number
        return repr



