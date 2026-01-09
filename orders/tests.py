from decimal import Decimal
from datetime import datetime, timedelta
from django.test import TestCase
from django.utils import timezone
from users.models import User
from orders.models import Order, OrderItem1, OrderItem2
from orders.reports import ReportService


class ReportServiceTestCase(TestCase):
    def setUp(self):
        self.base_date = datetime(2025, 1, 10, 12, 0, 0, tzinfo=timezone.utc)

        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123',
            is_active=True
        )
        self.user1.date_joined = self.base_date
        self.user1.save()

        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123',
            is_active=True
        )
        self.user2.date_joined = self.base_date + timedelta(days=1)
        self.user2.save()

        self.user3 = User.objects.create_user(
            username='user3',
            email='user3@example.com',
            password='testpass123',
            is_active=False
        )
        self.user3.date_joined = self.base_date + timedelta(days=1)
        self.user3.save()

        self.order1 = Order.objects.create(
            user=self.user1,
            created_at=self.base_date
        )
        self.order2 = Order.objects.create(
            user=self.user1,
            created_at=self.base_date
        )
        self.order3 = Order.objects.create(
            user=self.user2,
            created_at=self.base_date + timedelta(days=1)
        )
        OrderItem1.objects.create(
            order=self.order1,
            price=Decimal('100.00'),
            created_at=self.base_date
        )
        OrderItem1.objects.create(
            order=self.order1,
            price=Decimal('150.00'),
            created_at=self.base_date
        )
        OrderItem1.objects.create(
            order=self.order3,
            price=Decimal('75.50'),
            created_at=self.base_date + timedelta(days=1)
        )
        OrderItem2.objects.create(
            order=self.order2,
            placement_price=Decimal('50.00'),
            article_price=Decimal('30.00'),
            created_at=self.base_date
        )
        OrderItem2.objects.create(
            order=self.order2,
            placement_price=Decimal('25.00'),
            article_price=Decimal('15.00'),
            created_at=self.base_date
        )

    def test_daily_report(self):
        start_date = self.base_date
        end_date = self.base_date + timedelta(days=3)

        report = ReportService.generate_report(start_date, end_date, 'daily')

        self.assertEqual(len(report), 3)

        day1 = report[0]
        self.assertEqual(day1['NewUsers'], 1)
        self.assertEqual(day1['ActivatedUsers'], 1)
        self.assertEqual(day1['OrdersCount'], 2)
        self.assertEqual(day1['OrderItem1Count'], 2)
        self.assertEqual(day1['OrderItem1Amount'], 250.00)
        self.assertEqual(day1['OrderItem2Count'], 2)
        self.assertEqual(day1['OrderItem2Amount'], 120.00)
        self.assertEqual(day1['OrdersTotalAmount'], 370.00)

        day2 = report[1]
        self.assertEqual(day2['NewUsers'], 2)
        self.assertEqual(day2['ActivatedUsers'], 1)
        self.assertEqual(day2['OrdersCount'], 1)
        self.assertEqual(day2['OrderItem1Count'], 1)
        self.assertEqual(day2['OrderItem1Amount'], 75.50)
        self.assertEqual(day2['OrderItem2Count'], 0)
        self.assertEqual(day2['OrderItem2Amount'], 0.00)
        self.assertEqual(day2['OrdersTotalAmount'], 75.50)

        day3 = report[2]
        self.assertEqual(day3['NewUsers'], 0)
        self.assertEqual(day3['ActivatedUsers'], 0)
        self.assertEqual(day3['OrdersCount'], 0)
        self.assertEqual(day3['OrderItem1Count'], 0)
        self.assertEqual(day3['OrderItem1Amount'], 0.00)
        self.assertEqual(day3['OrderItem2Count'], 0)
        self.assertEqual(day3['OrderItem2Amount'], 0.00)
        self.assertEqual(day3['OrdersTotalAmount'], 0.00)

    def test_empty_date_range(self):
        start_date = self.base_date + timedelta(days=100)
        end_date = start_date + timedelta(days=5)

        report = ReportService.generate_report(start_date, end_date, 'daily')

        self.assertEqual(len(report), 5)

        for day in report:
            self.assertEqual(day['NewUsers'], 0)
            self.assertEqual(day['ActivatedUsers'], 0)
            self.assertEqual(day['OrdersCount'], 0)
            self.assertEqual(day['OrderItem1Count'], 0)
            self.assertEqual(day['OrderItem1Amount'], 0.00)
            self.assertEqual(day['OrderItem2Count'], 0)
            self.assertEqual(day['OrderItem2Amount'], 0.00)
            self.assertEqual(day['OrdersTotalAmount'], 0.00)

    def test_invalid_period_raises_error(self):
        with self.assertRaises(ValueError):
            ReportService.generate_report(
                self.base_date,
                self.base_date + timedelta(days=1),
                'invalid_period'
            )

    def test_report_data_structure(self):
        report = ReportService.generate_report(
            self.base_date,
            self.base_date + timedelta(days=1),
            'daily'
        )

        required_keys = [
            'Period', 'NewUsers', 'ActivatedUsers', 'OrdersCount',
            'OrderItem1Count', 'OrderItem1Amount',
            'OrderItem2Count', 'OrderItem2Amount',
            'OrdersTotalAmount'
        ]

        for day_data in report:
            for key in required_keys:
                self.assertIn(key, day_data)

    def test_amounts_are_float(self):
        report = ReportService.generate_report(
            self.base_date,
            self.base_date + timedelta(days=1),
            'daily'
        )

        day_data = report[0]
        self.assertIsInstance(day_data['OrderItem1Amount'], float)
        self.assertIsInstance(day_data['OrderItem2Amount'], float)
        self.assertIsInstance(day_data['OrdersTotalAmount'], float)
