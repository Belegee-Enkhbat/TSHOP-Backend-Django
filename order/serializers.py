from rest_framework import serializers

from .models import Order, OrderItem

from products.serializers import ProductSerializer


class MyOrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer

    class Meta:
        model = OrderItem
        fields = (
            "price",
            "product",
            "quantity",
        )


class MyOrderSerializer(serializers.ModelSerializer):
    items = MyOrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "address",
            "zipcode",
            "place",
            "phone",
            "stripe_token",
            "items",
            "paid_amount",
        )


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            "price",
            "product",
            "quantity",
        )


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "address",
            "zipcode",
            "place",
            "phone",
            "stripe_token",
            "items",
        )

    def create(self, validated_data: dict) -> Order:
        items_data = validated_data.pop("items")
        order = Order.objects.create(**validated_data)

        OrderItem.objects.bulk_create(
            [OrderItem(order=order, **item_data) for item_data in items_data]
        )
        return order
