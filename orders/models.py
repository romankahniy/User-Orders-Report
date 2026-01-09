import uuid
from django.db import models
from django.conf import settings


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='orders',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'orders_order'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"Order {self.id} by {self.user.email}"


class OrderItem1(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items1',
        on_delete=models.CASCADE
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'orders_orderitem1'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['order', 'created_at']),
        ]

    def __str__(self):
        return f"OrderItem1 for Order {self.order.id} - {self.price}"


class OrderItem2(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items2',
        on_delete=models.CASCADE
    )
    placement_price = models.DecimalField(max_digits=10, decimal_places=2)
    article_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'orders_orderitem2'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['order', 'created_at']),
        ]

    def __str__(self):
        total = self.placement_price + self.article_price
        return f"OrderItem2 for Order {self.order.id} - {total}"
