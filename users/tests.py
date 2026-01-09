from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from users.models import User
from orders.models import Order, OrderItem1, OrderItem2


class UserQuerySetTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="testpass123", is_active=True
        )

        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="testpass123", is_active=False
        )

        now = timezone.now()
        self.order1 = Order.objects.create(user=self.user1, created_at=now)
        self.order2 = Order.objects.create(user=self.user1, created_at=now)

        OrderItem1.objects.create(order=self.order1, price=Decimal("100.50"), created_at=now)
        OrderItem1.objects.create(order=self.order1, price=Decimal("50.25"), created_at=now)

        OrderItem2.objects.create(
            order=self.order1, placement_price=Decimal("30.00"), article_price=Decimal("20.00"), created_at=now
        )

        OrderItem2.objects.create(
            order=self.order2, placement_price=Decimal("15.00"), article_price=Decimal("10.00"), created_at=now
        )

    def test_with_orders_count(self):
        users = User.objects.with_orders_count()

        user1 = users.get(id=self.user1.id)
        user2 = users.get(id=self.user2.id)

        self.assertEqual(user1.orders_count, 2)
        self.assertEqual(user2.orders_count, 0)

    def test_with_orderitem1_count(self):
        users = User.objects.with_orderitem1_count()

        user1 = users.get(id=self.user1.id)
        user2 = users.get(id=self.user2.id)

        self.assertEqual(user1.orderitem1_count, 2)
        self.assertEqual(user2.orderitem1_count, 0)

    def test_with_orderitem2_count(self):
        users = User.objects.with_orderitem2_count()

        user1 = users.get(id=self.user1.id)
        user2 = users.get(id=self.user2.id)

        self.assertEqual(user1.orderitem2_count, 2)
        self.assertEqual(user2.orderitem2_count, 0)

    def test_with_total_spent(self):
        users = User.objects.with_total_spent()

        user1 = users.get(id=self.user1.id)
        user2 = users.get(id=self.user2.id)

        expected_total = Decimal("225.75")
        self.assertEqual(user1.total_spent, expected_total)
        self.assertEqual(user2.total_spent, Decimal("0"))

    def test_with_statistics(self):
        users = User.objects.with_statistics()

        user1 = users.get(id=self.user1.id)

        self.assertEqual(user1.orders_count, 2)
        self.assertEqual(user1.orderitem1_count, 2)
        self.assertEqual(user1.orderitem2_count, 2)

        self.assertEqual(user1.orderitem1_total, Decimal("150.75"))
        self.assertEqual(user1.orderitem2_total, Decimal("75.00"))
        self.assertEqual(user1.total_spent, Decimal("225.75"))

    def test_queryset_chaining(self):
        users = User.objects.filter(is_active=True).with_statistics()

        self.assertEqual(users.count(), 1)
        user = users.first()
        self.assertEqual(user.email, "user1@example.com")
        self.assertEqual(user.orders_count, 2)

    def test_empty_user_statistics(self):
        users = User.objects.with_statistics()
        user2 = users.get(id=self.user2.id)

        self.assertEqual(user2.orders_count, 0)
        self.assertEqual(user2.orderitem1_count, 0)
        self.assertEqual(user2.orderitem2_count, 0)
        self.assertEqual(user2.orderitem1_total, Decimal("0"))
        self.assertEqual(user2.orderitem2_total, Decimal("0"))
        self.assertEqual(user2.total_spent, Decimal("0"))
