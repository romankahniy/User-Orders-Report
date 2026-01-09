from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from orders.reports import ReportService, print_report


class Command(BaseCommand):
    help = 'Generate user activity and order statistics report'

    def add_arguments(self, parser):
        parser.add_argument(
            '--start-date',
            type=str,
            help='Start date (YYYY-MM-DD format). Defaults to 30 days ago.',
        )
        parser.add_argument(
            '--end-date',
            type=str,
            help='End date (YYYY-MM-DD format). Defaults to today.',
        )
        parser.add_argument(
            '--period',
            type=str,
            choices=['daily', 'weekly', 'monthly'],
            default='daily',
            help='Aggregation period (daily, weekly, or monthly). Default: daily',
        )

    def handle(self, *args, **options):
        if options['end_date']:
            end_date = datetime.strptime(options['end_date'], '%Y-%m-%d')
        else:
            end_date = datetime.now()

        if options['start_date']:
            start_date = datetime.strptime(options['start_date'], '%Y-%m-%d')
        else:
            start_date = end_date - timedelta(days=30)

        period = options['period']

        self.stdout.write(self.style.SUCCESS(
            f'Generating {period} report from {start_date.date()} to {end_date.date()}...'
        ))

        report_data = ReportService.generate_report(start_date, end_date, period)

        self.stdout.write('\n')
        print_report(report_data)

        self.stdout.write('\n')
        self.stdout.write(self.style.SUCCESS(
            f'Report generated successfully with {len(report_data)} periods'
        ))
