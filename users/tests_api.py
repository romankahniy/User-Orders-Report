from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from orders.models import Order, OrderItem1, OrderItem2


class UserAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="testpass123", is_active=True
        )

        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="testpass123", is_active=False
        )

        now = timezone.now()
        self.order1 = Order.objects.create(user=self.user1, created_at=now)

        OrderItem1.objects.create(order=self.order1, price=Decimal("100.50"), created_at=now)
        OrderItem2.objects.create(
            order=self.order1, placement_price=Decimal("30.00"), article_price=Decimal("20.00"), created_at=now
        )

    def test_list_users(self):
        url = reverse("user-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_retrieve_user(self):
        url = reverse("user-detail", kwargs={"pk": self.user1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "user1@example.com")
        self.assertEqual(response.data["username"], "user1")

    def test_filter_users_by_active(self):
        url = reverse("user-list")
        response = self.client.get(url, {"is_active": "true"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["email"], "user1@example.com")

    def test_search_users(self):
        url = reverse("user-list")
        response = self.client.get(url, {"search": "user1"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["email"], "user1@example.com")

    def test_users_statistics_endpoint(self):
        url = reverse("user-statistics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user1_data = None
        for user in response.data["results"]:
            if user["email"] == "user1@example.com":
                user1_data = user
                break

        self.assertIsNotNone(user1_data)
        self.assertEqual(user1_data["orders_count"], 1)
        self.assertEqual(user1_data["orderitem1_count"], 1)
        self.assertEqual(user1_data["orderitem2_count"], 1)
        self.assertEqual(float(user1_data["total_spent"]), 150.50)

    def test_user_statistics_detail(self):
        url = reverse("user-user-statistics", kwargs={"pk": self.user1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["orders_count"], 1)
        self.assertEqual(response.data["orderitem1_count"], 1)
        self.assertEqual(response.data["orderitem2_count"], 1)
        self.assertEqual(float(response.data["total_spent"]), 150.50)

    def test_ordering_users(self):
        url = reverse("user-list")
        response = self.client.get(url, {"ordering": "date_joined"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
