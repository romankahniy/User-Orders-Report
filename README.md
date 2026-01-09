# User & Orders Report - REST API

A Django REST Framework-based reporting system that provides RESTful API endpoints for user activity and order statistics with daily, weekly, and monthly aggregation.

## Features

- **RESTful API**: Complete REST API with Django REST Framework
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Custom User QuerySet**: Advanced querying capabilities with statistical annotations
- **Flexible Reporting**: Generate reports for daily, weekly, or monthly periods via API
- **Comprehensive Metrics**: Track user registrations, activations, orders, and revenue
- **Filtering & Search**: Built-in filtering, searching, and ordering
- **Docker Support**: Easy deployment with Docker Compose
- **PostgreSQL Database**: Production-ready database configuration
- **Environment-based Configuration**: All settings via environment variables
- **Full Test Coverage**: 100% API endpoint coverage

## Architecture

### Models

- **User**: Custom user model with UUID primary key
- **Order**: Orders associated with users
- **OrderItem1**: Order items with single price field
- **OrderItem2**: Order items with placement and article prices

### Custom QuerySet

The `UserQuerySet` provides advanced annotation methods:

- `with_orders_count()`: Annotate users with order count
- `with_orderitem1_count()`: Annotate users with OrderItem1 count
- `with_orderitem2_count()`: Annotate users with OrderItem2 count
- `with_total_spent()`: Annotate users with total spending
- `with_statistics()`: Comprehensive annotation with all metrics

### Report Metrics

| Metric              | Description                                    |
|---------------------|------------------------------------------------|
| NewUsers            | Number of registered users                     |
| ActivatedUsers      | Users with `is_active = True`                  |
| OrdersCount         | Number of created orders                       |
| OrderItem1Count     | Count of OrderItem1 entries                    |
| OrderItem1Amount    | Sum of OrderItem1.price                        |
| OrderItem2Count     | Count of OrderItem2 entries                    |
| OrderItem2Amount    | Sum of placement_price + article_price         |
| OrdersTotalAmount   | Total sum across all order item types          |

## Quick Start

### Option 1: Automated Setup (Recommended)

Run the quickstart script that does everything automatically:

```bash
chmod +x quickstart.sh
./quickstart.sh
```

This will:
- Start Docker containers
- Run database migrations
- Generate sample data (30 users, 10 days)
- Run all tests
- Display API URLs

### Option 2: Manual Setup

**1. Start the application:**
```bash
docker compose up -d
```

**2. Create migrations (if needed):**
```bash
# Create migrations for users app
docker compose exec web python manage.py makemigrations users

# Create migrations for orders app
docker compose exec web python manage.py makemigrations orders
```

**3. Run migrations:**
```bash
docker compose exec web python manage.py migrate
```

**4. Generate sample data:**
```bash
docker compose exec web python manage.py generate_sample_data --users 50 --days 30
```

**5. Run tests:**
```bash
docker compose exec web python manage.py test
```

**6. Access the API:**
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- API Root: http://localhost:8000/api/

## Prerequisites

- Docker
- Docker Compose


## Usage

### Generating Sample Data

Before generating reports, you can create test data:

```bash
# Generate 50 users with data over 30 days
docker compose exec web python manage.py generate_sample_data --users 50 --days 30

# Generate 100 users with data over 7 days
docker compose exec web python manage.py generate_sample_data --users 100 --days 7
```

### API Documentation

Once the application is running, you can access:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### API Endpoints

#### Users
- `GET /api/users/` - List all users
- `GET /api/users/{id}/` - Get specific user
- `GET /api/users/statistics/` - Get all users with statistics
- `GET /api/users/{id}/user_statistics/` - Get specific user statistics

**Example:**
```bash
# List users
curl http://localhost:8000/api/users/

# Get user statistics
curl http://localhost:8000/api/users/statistics/

# Filter active users
curl http://localhost:8000/api/users/?is_active=true

# Search users
curl http://localhost:8000/api/users/?search=john
```

#### Orders
- `GET /api/orders/` - List all orders
- `GET /api/orders/{id}/` - Get specific order with items
- `GET /api/order-items1/` - List OrderItem1 entries
- `GET /api/order-items2/` - List OrderItem2 entries

**Example:**
```bash
# List orders
curl http://localhost:8000/api/orders/

# Get order details with items
curl http://localhost:8000/api/orders/{order_id}/

# Filter orders by user
curl http://localhost:8000/api/orders/?user={user_id}
```

#### Reports
- `GET /api/reports/daily/` - Generate daily report
- `GET /api/reports/weekly/` - Generate weekly report
- `GET /api/reports/monthly/` - Generate monthly report

**Query Parameters:**
- `start_date` - Start date (YYYY-MM-DD), defaults to 30 days ago
- `end_date` - End date (YYYY-MM-DD), defaults to today

**Example:**
```bash
# Daily report (last 30 days)
curl http://localhost:8000/api/reports/daily/

# Daily report with custom dates
curl "http://localhost:8000/api/reports/daily/?start_date=2025-01-01&end_date=2025-01-31"

# Weekly report
curl "http://localhost:8000/api/reports/weekly/?start_date=2025-01-01&end_date=2025-01-31"

# Monthly report
curl "http://localhost:8000/api/reports/monthly/?start_date=2025-01-01&end_date=2025-03-01"
```

**Response Format:**
```json
{
  "period": "daily",
  "start_date": "2025-01-01",
  "end_date": "2025-01-31",
  "data": [
    {
      "Period": "2025-01-10",
      "NewUsers": 12,
      "ActivatedUsers": 5,
      "OrdersCount": 7,
      "OrderItem1Count": 6,
      "OrderItem1Amount": 410.00,
      "OrderItem2Count": 3,
      "OrderItem2Amount": 350.00,
      "OrdersTotalAmount": 760.00
    },
    ...
  ]
}
```

### Creating Test Data (Console)

You can use the Django shell to create test data:

```bash
docker compose exec web python manage.py shell
```

Then in the shell:

```python
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone
from users.models import User
from orders.models import Order, OrderItem1, OrderItem2

# Create a user
user = User.objects.create_user(
    username='testuser',
    email='test@example.com',
    password='testpass123',
    is_active=True
)

# Create an order
now = timezone.now()
order = Order.objects.create(user=user, created_at=now)

# Create order items
OrderItem1.objects.create(
    order=order,
    price=Decimal('100.00'),
    created_at=now
)

OrderItem2.objects.create(
    order=order,
    placement_price=Decimal('50.00'),
    article_price=Decimal('30.00'),
    created_at=now
)
```

### Generating Reports

#### Daily Report

```bash
docker compose exec web python manage.py generate_report --period daily
```

#### Weekly Report

```bash
docker compose exec web python manage.py generate_report --period weekly
```

#### Monthly Report

```bash
docker compose exec web python manage.py generate_report --period monthly
```

#### Custom Date Range

```bash
docker compose exec web python manage.py generate_report \
    --start-date 2025-01-01 \
    --end-date 2025-01-31 \
    --period daily
```

### Example Output

```
Period       | NewUsers | ActivatedUsers | OrdersCount | Item1Count | Item1Amount | Item2Count | Item2Amount | TotalAmount
---------------------------------------------------------------------------------------------------------------------------------
2025-01-10   | 12       | 5              | 7           | 6          | 410.00      | 3          | 350.00      | 760.00     
2025-01-11   | 4        | 3              | 1           | 2          | 120.00      | 0          | 0.00        | 120.00     
2025-01-12   | 0        | 0              | 0           | 0          | 0.00        | 0          | 0.00        | 0.00       
```

### Using the Custom QuerySet

```python
from users.models import User

# Get users with full statistics
users = User.objects.with_statistics()
for user in users:
    print(f"{user.email}: {user.orders_count} orders, ${user.total_spent} spent")

# Get users with specific annotations
active_users = User.objects.filter(is_active=True).with_orders_count()

# Chain with other QuerySet methods
big_spenders = User.objects.with_total_spent().filter(total_spent__gt=1000)
```

## Development

### Project Structure

```
user-orders-report/
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Application container definition
├── requirements.txt        # Python dependencies (+ DRF)
├── manage.py               # Django management script
├── reporting/              # Django project settings
│   ├── settings.py        # Settings with REST Framework config
│   ├── urls.py            # Main URL routing with API docs
│   └── wsgi.py
├── users/                  # Users application
│   ├── models.py          # User model with custom QuerySet
│   ├── serializers.py     # 🆕 DRF serializers for User
│   ├── views.py           # 🆕 DRF ViewSets for User API
│   ├── urls.py            # 🆕 User API URLs
│   ├── admin.py
│   ├── tests.py           # User QuerySet tests
│   └── tests_api.py       # 🆕 User API tests
└── orders/                 # Orders application
    ├── models.py          # Order models
    ├── serializers.py     # 🆕 DRF serializers for Orders
    ├── views.py           # 🆕 DRF ViewSets for Orders & Reports
    ├── urls.py            # 🆕 Orders API URLs
    ├── reports.py         # Report generation service
    ├── admin.py
    ├── tests.py           # Report service tests
    ├── tests_api.py       # 🆕 Orders & Reports API tests
    └── management/
        └── commands/
            ├── generate_report.py        # CLI command
            └── generate_sample_data.py   # Test data generator
```

### Running the Development Server

```bash
docker compose up
```

The application will be available at http://localhost:8000

### Accessing the Database

```bash
docker compose exec db psql -U reporting_user -d reporting_db
```

### Viewing Logs

```bash
docker compose logs -f web
```

### Stopping the Application

```bash
docker compose down
```

To remove volumes as well:

```bash
docker compose down -v
```

## Testing

The project includes comprehensive test coverage for both the QuerySet layer and REST API:

- **User QuerySet Tests** (users/tests.py): 8 tests
- **User API Tests** (users/tests_api.py): 8 tests
- **Report Service Tests** (orders/tests.py): 9 tests
- **Orders & Reports API Tests** (orders/tests_api.py): 10 tests

**Total: 35 test cases**

Run all tests:

```bash
docker compose exec web python manage.py test
```

Run specific test modules:

```bash
# Test only User QuerySet
docker compose exec web python manage.py test users.tests

# Test only Report Service
docker compose exec web python manage.py test orders.tests
```

Run with verbose output:

```bash
docker compose exec web python manage.py test --verbosity=2
```

## Environment Variables

| Variable      | Description                    | Default           |
|---------------|--------------------------------|-------------------|
| DEBUG         | Django debug mode              | True              |
| SECRET_KEY    | Django secret key              | (development key) |
| DB_NAME       | PostgreSQL database name       | reporting_db      |
| DB_USER       | PostgreSQL username            | reporting_user    |
| DB_PASSWORD   | PostgreSQL password            | reporting_pass    |
| DB_HOST       | PostgreSQL host                | db                |
| DB_PORT       | PostgreSQL port                | 5432              |

## Admin Interface

Create a superuser to access the Django admin:

```bash
docker compose exec web python manage.py createsuperuser
```

Then access the admin at http://localhost:8000/admin

## Production Considerations

For production deployment:

1. Change `SECRET_KEY` to a secure random value
2. Set `DEBUG=False`
3. Configure `ALLOWED_HOSTS` in settings
4. Use strong database credentials
5. Set up proper SSL/TLS certificates
6. Configure static file serving
7. Set up proper logging
8. Use a production WSGI server (gunicorn, uWSGI)
