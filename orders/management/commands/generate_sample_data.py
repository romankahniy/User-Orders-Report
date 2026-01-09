from datetime import timedelta
from decimal import Decimal
from random import choice, randint

from django.core.management.base import BaseCommand
from django.utils import timezone

from orders.models import Order, OrderItem1, OrderItem2
from users.models import User


class Command(BaseCommand):
    help = "Generate sample data for testing reports"

    def add_arguments(self, parser):
        parser.add_argument(
            "--users",
            type=int,
            default=10,
            help="Number of users to create. Default: 10",
        )
        parser.add_argument(
            "--days",
            type=int,
            default=7,
            help="Number of days to spread data across. Default: 7",
        )

    def handle(self, *args, **options):
        num_users = options["users"]
        num_days = options["days"]

        self.stdout.write(self.style.SUCCESS(f"Generating sample data: {num_users} users over {num_days} days..."))

        base_date = timezone.now() - timedelta(days=num_days)

        users_created = 0
        orders_created = 0
        items1_created = 0
        items2_created = 0

        for i in range(num_users):
            days_offset = randint(0, num_days - 1)
            user_date = base_date + timedelta(days=days_offset)

            username = f"testuser{i + 1}"
            email = f"test{i + 1}@example.com"

            if User.objects.filter(email=email).exists():
                self.stdout.write(self.style.WARNING(f"User {email} already exists, skipping..."))
                continue

            user = User.objects.create_user(
                username=username, email=email, password="testpass123", is_active=choice([True, False])
            )
            user.date_joined = user_date
            user.save()
            users_created += 1

            num_orders = randint(0, 3)
            for _ in range(num_orders):
                order_date = user_date + timedelta(hours=randint(0, 23), minutes=randint(0, 59))

                order = Order.objects.create(user=user, created_at=order_date)
                orders_created += 1

                num_items1 = randint(0, 3)
                for _ in range(num_items1):
                    item_date = order_date + timedelta(minutes=randint(1, 30))
                    OrderItem1.objects.create(
                        order=order, price=Decimal(str(randint(10, 500))) + Decimal("0.50"), created_at=item_date
                    )
                    items1_created += 1

                num_items2 = randint(0, 2)
                for _ in range(num_items2):
                    item_date = order_date + timedelta(minutes=randint(1, 30))
                    OrderItem2.objects.create(
                        order=order,
                        placement_price=Decimal(str(randint(5, 100))) + Decimal("0.25"),
                        article_price=Decimal(str(randint(5, 100))) + Decimal("0.75"),
                        created_at=item_date,
                    )
                    items2_created += 1

        self.stdout.write(self.style.SUCCESS("\nSample data generated successfully!"))
        self.stdout.write(f"Users created: {users_created}")
        self.stdout.write(f"Orders created: {orders_created}")
        self.stdout.write(f"OrderItem1 created: {items1_created}")
        self.stdout.write(f"OrderItem2 created: {items2_created}")

        self.stdout.write(self.style.SUCCESS("\nYou can now generate reports using:"))
        self.stdout.write("python manage.py generate_report --period daily")
