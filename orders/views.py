from datetime import datetime, timedelta
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import Order, OrderItem1, OrderItem2
from .serializers import (
    OrderSerializer,
    OrderDetailSerializer,
    OrderItem1Serializer,
    OrderItem2Serializer,
    ReportSerializer
)
from .reports import ReportService


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'created_at']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderSerializer


class OrderItem1ViewSet(viewsets.ModelViewSet):
    queryset = OrderItem1.objects.all()
    serializer_class = OrderItem1Serializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['order', 'created_at']
    ordering_fields = ['created_at', 'price']
    ordering = ['-created_at']


class OrderItem2ViewSet(viewsets.ModelViewSet):
    queryset = OrderItem2.objects.all()
    serializer_class = OrderItem2Serializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['order', 'created_at']
    ordering_fields = ['created_at', 'placement_price', 'article_price']
    ordering = ['-created_at']


class ReportViewSet(viewsets.ViewSet):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='start_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Start date (YYYY-MM-DD). Defaults to 30 days ago.',
                required=False,
            ),
            OpenApiParameter(
                name='end_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='End date (YYYY-MM-DD). Defaults to today.',
                required=False,
            ),
        ],
        responses={200: ReportSerializer(many=True)},
    )
    @action(detail=False, methods=['get'])
    def daily(self, request):
        start_date, end_date = self._parse_dates(request)

        report_data = ReportService.generate_report(
            start_date,
            end_date,
            'daily'
        )

        serializer = ReportSerializer(report_data, many=True)
        return Response({
            'period': 'daily',
            'start_date': start_date.date().isoformat(),
            'end_date': end_date.date().isoformat(),
            'data': serializer.data
        })

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='start_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Start date (YYYY-MM-DD). Defaults to 30 days ago.',
                required=False,
            ),
            OpenApiParameter(
                name='end_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='End date (YYYY-MM-DD). Defaults to today.',
                required=False,
            ),
        ],
        responses={200: ReportSerializer(many=True)},
    )
    @action(detail=False, methods=['get'])
    def weekly(self, request):
        start_date, end_date = self._parse_dates(request)

        report_data = ReportService.generate_report(
            start_date,
            end_date,
            'weekly'
        )

        serializer = ReportSerializer(report_data, many=True)
        return Response({
            'period': 'weekly',
            'start_date': start_date.date().isoformat(),
            'end_date': end_date.date().isoformat(),
            'data': serializer.data
        })

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='start_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Start date (YYYY-MM-DD). Defaults to 30 days ago.',
                required=False,
            ),
            OpenApiParameter(
                name='end_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='End date (YYYY-MM-DD). Defaults to today.',
                required=False,
            ),
        ],
        responses={200: ReportSerializer(many=True)},
    )
    @action(detail=False, methods=['get'])
    def monthly(self, request):
        start_date, end_date = self._parse_dates(request)

        report_data = ReportService.generate_report(
            start_date,
            end_date,
            'monthly'
        )

        serializer = ReportSerializer(report_data, many=True)
        return Response({
            'period': 'monthly',
            'start_date': start_date.date().isoformat(),
            'end_date': end_date.date().isoformat(),
            'data': serializer.data
        })

    def _parse_dates(self, request):
        end_date_str = request.query_params.get('end_date')
        start_date_str = request.query_params.get('start_date')

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            except ValueError:
                end_date = datetime.now()
        else:
            end_date = datetime.now()

        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            except ValueError:
                start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=30)

        return start_date, end_date
