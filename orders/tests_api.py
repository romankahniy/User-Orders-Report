from decimal import Decimal
from datetime import datetime, timedelta
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from orders.models import Order, OrderItem1, OrderItem2


class OrderAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_active=True
        )

        now = timezone.now()
        self.order1 = Order.objects.create(user=self.user, created_at=now)
        self.order2 = Order.objects.create(
            user=self.user,
            created_at=now - timedelta(days=1)
        )

        self.item1 = OrderItem1.objects.create(
            order=self.order1,
            price=Decimal('100.00'),
            created_at=now
        )
        self.item2 = OrderItem2.objects.create(
            order=self.order1,
            placement_price=Decimal('50.00'),
            article_price=Decimal('30.00'),
            created_at=now
        )

    def test_list_orders(self):
        url = reverse('order-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_retrieve_order_detail(self):
        url = reverse('order-detail', kwargs={'pk': self.order1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items1']), 1)
        self.assertEqual(len(response.data['items2']), 1)
        self.assertEqual(response.data['user_email'], 'test@example.com')

    def test_filter_orders_by_user(self):
        url = reverse('order-list')
        response = self.client.get(url, {'user': self.user.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_list_orderitems1(self):
        url = reverse('orderitem1-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(float(response.data['results'][0]['price']), 100.00)

    def test_list_orderitems2(self):
        url = reverse('orderitem2-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        result = response.data['results'][0]
        self.assertEqual(float(result['placement_price']), 50.00)
        self.assertEqual(float(result['article_price']), 30.00)
        self.assertEqual(result['total_price'], 80.00)


class ReportAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        base_date = datetime(2025, 1, 10, 12, 0, 0, tzinfo=timezone.utc)

        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123',
            is_active=True
        )
        self.user1.date_joined = base_date
        self.user1.save()

        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123',
            is_active=False
        )
        self.user2.date_joined = base_date + timedelta(days=1)
        self.user2.save()

        self.order1 = Order.objects.create(
            user=self.user1,
            created_at=base_date
        )
        self.order2 = Order.objects.create(
            user=self.user2,
            created_at=base_date + timedelta(days=1)
        )

        OrderItem1.objects.create(
            order=self.order1,
            price=Decimal('100.00'),
            created_at=base_date
        )
        OrderItem2.objects.create(
            order=self.order2,
            placement_price=Decimal('50.00'),
            article_price=Decimal('30.00'),
            created_at=base_date + timedelta(days=1)
        )

    def test_daily_report(self):
        url = reverse('report-daily')
        response = self.client.get(url, {
            'start_date': '2025-01-10',
            'end_date': '2025-01-13'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['period'], 'daily')
        self.assertEqual(len(response.data['data']), 3)

        day1 = response.data['data'][0]
        self.assertEqual(day1['NewUsers'], 1)
        self.assertEqual(day1['ActivatedUsers'], 1)
        self.assertEqual(day1['OrdersCount'], 1)
        self.assertEqual(day1['OrderItem1Count'], 1)
        self.assertEqual(day1['OrderItem1Amount'], 100.00)

    def test_weekly_report(self):
        url = reverse('report-weekly')
        response = self.client.get(url, {
            'start_date': '2025-01-05',
            'end_date': '2025-01-20'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['period'], 'weekly')
        self.assertGreater(len(response.data['data']), 0)

    def test_monthly_report(self):
        url = reverse('report-monthly')
        response = self.client.get(url, {
            'start_date': '2025-01-01',
            'end_date': '2025-03-01'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['period'], 'monthly')
        self.assertGreater(len(response.data['data']), 0)

    def test_report_without_dates(self):
        url = reverse('report-daily')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('start_date', response.data)
        self.assertIn('end_date', response.data)

    def test_report_data_structure(self):
        url = reverse('report-daily')
        response = self.client.get(url, {
            'start_date': '2025-01-10',
            'end_date': '2025-01-11'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        required_keys = [
            'Period', 'NewUsers', 'ActivatedUsers', 'OrdersCount',
            'OrderItem1Count', 'OrderItem1Amount',
            'OrderItem2Count', 'OrderItem2Amount',
            'OrdersTotalAmount'
        ]

        for day_data in response.data['data']:
            for key in required_keys:
                self.assertIn(key, day_data)
