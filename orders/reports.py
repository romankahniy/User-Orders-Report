from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Literal
from django.db.models import Count, Sum, Q, F, DecimalField
from django.db.models.functions import Coalesce, TruncDate, TruncWeek, TruncMonth
from users.models import User
from orders.models import Order, OrderItem1, OrderItem2

PeriodType = Literal["daily", "weekly", "monthly"]


class ReportService:
    @staticmethod
    def generate_report(start_date: datetime, end_date: datetime, period: PeriodType = "daily") -> List[Dict[str, Any]]:
        trunc_functions = {
            "daily": TruncDate,
            "weekly": TruncWeek,
            "monthly": TruncMonth,
        }

        if period not in trunc_functions:
            raise ValueError(f"Invalid period: {period}. Must be 'daily', 'weekly', or 'monthly'")

        trunc_func = trunc_functions[period]
        user_stats = ReportService._get_user_statistics(start_date, end_date, trunc_func)
        order_stats = ReportService._get_order_statistics(start_date, end_date, trunc_func)
        item1_stats = ReportService._get_orderitem1_statistics(start_date, end_date, trunc_func)
        item2_stats = ReportService._get_orderitem2_statistics(start_date, end_date, trunc_func)

        result = ReportService._merge_statistics(
            user_stats, order_stats, item1_stats, item2_stats, start_date, end_date, period
        )

        return result

    @staticmethod
    def _get_user_statistics(start_date: datetime, end_date: datetime, trunc_func) -> Dict[str, Dict]:
        users = (
            User.objects.filter(date_joined__gte=start_date, date_joined__lt=end_date)
            .annotate(period=trunc_func("date_joined"))
            .values("period")
            .annotate(new_users=Count("id"), activated_users=Count("id", filter=Q(is_active=True)))
        )

        return {str(u["period"]): u for u in users}

    @staticmethod
    def _get_order_statistics(start_date: datetime, end_date: datetime, trunc_func) -> Dict[str, Dict]:
        orders = (
            Order.objects.filter(created_at__gte=start_date, created_at__lt=end_date)
            .annotate(period=trunc_func("created_at"))
            .values("period")
            .annotate(orders_count=Count("id"))
        )

        return {str(o["period"]): o for o in orders}

    @staticmethod
    def _get_orderitem1_statistics(start_date: datetime, end_date: datetime, trunc_func) -> Dict[str, Dict]:
        items1 = (
            OrderItem1.objects.filter(created_at__gte=start_date, created_at__lt=end_date)
            .annotate(period=trunc_func("created_at"))
            .values("period")
            .annotate(
                orderitem1_count=Count("id"),
                orderitem1_amount=Coalesce(Sum("price"), Decimal("0"), output_field=DecimalField()),
            )
        )

        return {str(i["period"]): i for i in items1}

    @staticmethod
    def _get_orderitem2_statistics(start_date: datetime, end_date: datetime, trunc_func) -> Dict[str, Dict]:
        items2 = (
            OrderItem2.objects.filter(created_at__gte=start_date, created_at__lt=end_date)
            .annotate(period=trunc_func("created_at"))
            .values("period")
            .annotate(
                orderitem2_count=Count("id"),
                orderitem2_amount=Coalesce(
                    Sum(F("placement_price") + F("article_price"), output_field=DecimalField()),
                    Decimal("0"),
                    output_field=DecimalField(),
                ),
            )
        )

        return {str(i["period"]): i for i in items2}

    @staticmethod
    def _merge_statistics(
        user_stats: Dict,
        order_stats: Dict,
        item1_stats: Dict,
        item2_stats: Dict,
        start_date: datetime,
        end_date: datetime,
        period: PeriodType,
    ) -> List[Dict[str, Any]]:
        all_periods = ReportService._generate_all_periods(start_date, end_date, period)

        result = []
        for period_date in all_periods:
            period_key = str(period_date)

            user_data = user_stats.get(period_key, {})
            order_data = order_stats.get(period_key, {})
            item1_data = item1_stats.get(period_key, {})
            item2_data = item2_stats.get(period_key, {})

            new_users = user_data.get("new_users", 0)
            activated_users = user_data.get("activated_users", 0)
            orders_count = order_data.get("orders_count", 0)

            orderitem1_count = item1_data.get("orderitem1_count", 0)
            orderitem1_amount = item1_data.get("orderitem1_amount", Decimal("0"))

            orderitem2_count = item2_data.get("orderitem2_count", 0)
            orderitem2_amount = item2_data.get("orderitem2_amount", Decimal("0"))

            orders_total_amount = orderitem1_amount + orderitem2_amount

            result.append(
                {
                    "Period": period_key,
                    "NewUsers": new_users,
                    "ActivatedUsers": activated_users,
                    "OrdersCount": orders_count,
                    "OrderItem1Count": orderitem1_count,
                    "OrderItem1Amount": float(orderitem1_amount),
                    "OrderItem2Count": orderitem2_count,
                    "OrderItem2Amount": float(orderitem2_amount),
                    "OrdersTotalAmount": float(orders_total_amount),
                }
            )

        return result

    @staticmethod
    def _generate_all_periods(start_date: datetime, end_date: datetime, period: PeriodType) -> List[datetime]:
        periods = []
        current = start_date

        if period == "daily":
            while current < end_date:
                periods.append(current.date())
                current += timedelta(days=1)

        elif period == "weekly":
            current = current - timedelta(days=current.weekday())
            while current < end_date:
                periods.append(current.date())
                current += timedelta(weeks=1)

        elif period == "monthly":
            current = current.replace(day=1)
            while current < end_date:
                periods.append(current.date())
                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1)
                else:
                    current = current.replace(month=current.month + 1)

        return periods


def print_report(report_data: List[Dict[str, Any]]) -> None:
    if not report_data:
        print("No data to display")
        return

    headers = [
        "Period",
        "NewUsers",
        "ActivatedUsers",
        "OrdersCount",
        "Item1Count",
        "Item1Amount",
        "Item2Count",
        "Item2Amount",
        "TotalAmount",
    ]

    col_widths = {h: len(h) for h in headers}
    for row in report_data:
        col_widths["Period"] = max(col_widths["Period"], len(str(row["Period"])))
        for key in headers[1:]:
            col_widths[key] = max(col_widths[key], len(str(row.get(key.replace("Item", "OrderItem"), row.get(key, 0)))))

    header_row = " | ".join(h.ljust(col_widths[headers[i]]) for i, h in enumerate(headers))
    print(header_row)
    print("-" * len(header_row))

    for row in report_data:
        values = [
            str(row["Period"]).ljust(col_widths["Period"]),
            str(row["NewUsers"]).ljust(col_widths["NewUsers"]),
            str(row["ActivatedUsers"]).ljust(col_widths["ActivatedUsers"]),
            str(row["OrdersCount"]).ljust(col_widths["OrdersCount"]),
            str(row["OrderItem1Count"]).ljust(col_widths["Item1Count"]),
            f"{row['OrderItem1Amount']:.2f}".ljust(col_widths["Item1Amount"]),
            str(row["OrderItem2Count"]).ljust(col_widths["Item2Count"]),
            f"{row['OrderItem2Amount']:.2f}".ljust(col_widths["Item2Amount"]),
            f"{row['OrdersTotalAmount']:.2f}".ljust(col_widths["TotalAmount"]),
        ]
        print(" | ".join(values))
