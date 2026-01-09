from rest_framework import serializers
from .models import Order, OrderItem1, OrderItem2


class OrderItem1Serializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem1
        fields = ['id', 'order', 'price', 'created_at']
        read_only_fields = ['id']


class OrderItem2Serializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem2
        fields = ['id', 'order', 'placement_price', 'article_price', 'total_price', 'created_at']
        read_only_fields = ['id']

    def get_total_price(self, obj):
        return obj.placement_price + obj.article_price


class OrderSerializer(serializers.ModelSerializer):
    items1_count = serializers.SerializerMethodField()
    items2_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'items1_count', 'items2_count']
        read_only_fields = ['id']

    def get_items1_count(self, obj):
        return obj.items1.count()

    def get_items2_count(self, obj):
        return obj.items2.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    items1 = OrderItem1Serializer(many=True, read_only=True)
    items2 = OrderItem2Serializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'user_email', 'created_at', 'items1', 'items2']
        read_only_fields = ['id']


class ReportSerializer(serializers.Serializer):
    Period = serializers.CharField()
    NewUsers = serializers.IntegerField()
    ActivatedUsers = serializers.IntegerField()
    OrdersCount = serializers.IntegerField()
    OrderItem1Count = serializers.IntegerField()
    OrderItem1Amount = serializers.FloatField()
    OrderItem2Count = serializers.IntegerField()
    OrderItem2Amount = serializers.FloatField()
    OrdersTotalAmount = serializers.FloatField()
