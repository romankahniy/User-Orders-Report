#!/bin/bash

set -e

echo "=========================================="
echo "User & Orders Report - Quick Start"
echo "=========================================="
echo ""

if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "Please start Docker and try again"
    exit 1
fi

echo "✅ Docker is running"
echo ""

echo "📦 Starting services..."
docker compose up -d

echo "⏳ Waiting for database to be ready..."
sleep 5

echo "📝 Creating migrations..."
docker compose exec -T web python manage.py makemigrations users || echo "Users migrations already exist"
docker compose exec -T web python manage.py makemigrations orders || echo "Orders migrations already exist"

echo "🔄 Running database migrations..."
docker compose exec -T web python manage.py migrate

echo "🎲 Generating sample data..."
docker compose exec -T web python manage.py generate_sample_data --users 30 --days 10

echo "🧪 Running tests..."
docker compose exec -T web python manage.py test

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "🌐 Application URLs:"
echo "-------------------"
echo "API Base: http://localhost:8000/api/"
echo "Swagger UI: http://localhost:8000/api/docs/"
echo "ReDoc: http://localhost:8000/api/redoc/"
echo "Django Admin: http://localhost:8000/admin/"
echo ""
echo "Quick Commands:"
echo "---------------"
echo ""
echo "API Examples (using curl):"
echo "  # List users"
echo "  curl http://localhost:8000/api/users/"
echo ""
echo "  # Get users with statistics"
echo "  curl http://localhost:8000/api/users/statistics/"
echo ""
echo "  # Generate daily report"
echo "  curl http://localhost:8000/api/reports/daily/"
echo ""
echo "  # Generate report with date range"
echo "  curl \"http://localhost:8000/api/reports/daily/?start_date=2025-01-01&end_date=2025-01-31\""
echo ""
echo "CLI Commands:"
echo "-------------"
echo ""
echo "Generate daily report (CLI):"
echo "  docker compose exec web python manage.py generate_report --period daily"
echo ""
echo "Generate weekly report (CLI):"
echo "  docker compose exec web python manage.py generate_report --period weekly"
echo ""
echo "Generate monthly report (CLI):"
echo "  docker compose exec web python manage.py generate_report --period monthly"
echo ""
echo "Create superuser (admin access):"
echo "  docker compose exec web python manage.py createsuperuser"
echo ""
echo "Access Django shell:"
echo "  docker compose exec web python manage.py shell"
echo ""
echo "View logs:"
echo "  docker compose logs -f web"
echo ""
echo "Stop services:"
echo "  docker compose down"
echo ""
echo "=========================================="
