from django.contrib import admin
from .models import Order, OrderItem1, OrderItem2


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__email", "id")
    ordering = ("-created_at",)
    raw_id_fields = ("user",)


@admin.register(OrderItem1)
class OrderItem1Admin(admin.ModelAdmin):
    list_display = ("id", "order", "price", "created_at")
    list_filter = ("created_at",)
    search_fields = ("order__id",)
    ordering = ("-created_at",)
    raw_id_fields = ("order",)


@admin.register(OrderItem2)
class OrderItem2Admin(admin.ModelAdmin):
    list_display = ("id", "order", "placement_price", "article_price", "total_price", "created_at")
    list_filter = ("created_at",)
    search_fields = ("order__id",)
    ordering = ("-created_at",)
    raw_id_fields = ("order",)

    def total_price(self, obj):
        return obj.placement_price + obj.article_price

    total_price.short_description = "Total Price"
