from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, OrderItem1ViewSet, OrderItem2ViewSet, ReportViewSet


router = DefaultRouter()
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"order-items1", OrderItem1ViewSet, basename="orderitem1")
router.register(r"order-items2", OrderItem2ViewSet, basename="orderitem2")
router.register(r"reports", ReportViewSet, basename="report")

urlpatterns = [
    path("", include(router.urls)),
]
