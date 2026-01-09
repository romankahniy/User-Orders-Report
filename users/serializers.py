from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "is_active", "date_joined"]
        read_only_fields = ["id", "date_joined"]


class UserStatisticsSerializer(serializers.ModelSerializer):
    orders_count = serializers.IntegerField(read_only=True)
    orderitem1_count = serializers.IntegerField(read_only=True)
    orderitem2_count = serializers.IntegerField(read_only=True)
    total_spent = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "is_active",
            "date_joined",
            "orders_count",
            "orderitem1_count",
            "orderitem2_count",
            "total_spent",
        ]
        read_only_fields = ["id", "date_joined"]
