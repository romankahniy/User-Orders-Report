import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Count, DecimalField, F, Sum
from django.db.models.functions import Coalesce


class UserQuerySet(models.QuerySet):
    def with_statistics(self):
        return self.annotate(
            orders_count=Count("orders", distinct=True),
            orderitem1_count=Count("orders__items1", distinct=True),
            orderitem2_count=Count("orders__items2", distinct=True),
            orderitem1_total=Coalesce(Sum("orders__items1__price", distinct=True), 0, output_field=DecimalField()),
            orderitem2_placement_total=Coalesce(
                Sum("orders__items2__placement_price", distinct=True), 0, output_field=DecimalField()
            ),
            orderitem2_article_total=Coalesce(
                Sum("orders__items2__article_price", distinct=True), 0, output_field=DecimalField()
            ),
        ).annotate(
            orderitem2_total=F("orderitem2_placement_total") + F("orderitem2_article_total"),
            total_spent=F("orderitem1_total") + F("orderitem2_placement_total") + F("orderitem2_article_total"),
        )

    def with_orders_count(self):
        return self.annotate(orders_count=Count("orders", distinct=True))

    def with_orderitem1_count(self):
        return self.annotate(orderitem1_count=Count("orders__items1", distinct=True))

    def with_orderitem2_count(self):
        return self.annotate(orderitem2_count=Count("orders__items2", distinct=True))

    def with_total_spent(self):
        return self.annotate(
            orderitem1_total=Coalesce(Sum("orders__items1__price", distinct=True), 0, output_field=DecimalField()),
            orderitem2_placement_total=Coalesce(
                Sum("orders__items2__placement_price", distinct=True), 0, output_field=DecimalField()
            ),
            orderitem2_article_total=Coalesce(
                Sum("orders__items2__article_price", distinct=True), 0, output_field=DecimalField()
            ),
        ).annotate(total_spent=F("orderitem1_total") + F("orderitem2_placement_total") + F("orderitem2_article_total"))


class UserManager(models.Manager):
    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    def normalize_email(self, email):
        email = email or ""
        try:
            email_name, domain_part = email.strip().rsplit("@", 1)
        except ValueError:
            pass
        else:
            email = email_name + "@" + domain_part.lower()
        return email

    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)

    def with_statistics(self):
        return self.get_queryset().with_statistics()

    def with_orders_count(self):
        return self.get_queryset().with_orders_count()

    def with_orderitem1_count(self):
        return self.get_queryset().with_orderitem1_count()

    def with_orderitem2_count(self):
        return self.get_queryset().with_orderitem2_count()

    def with_total_spent(self):
        return self.get_queryset().with_total_spent()


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    class Meta:
        db_table = "users_user"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email
