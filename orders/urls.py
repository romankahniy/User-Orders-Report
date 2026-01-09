from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import OrderItem1ViewSet, OrderItem2ViewSet, OrderViewSet, ReportViewSet

router = DefaultRouter()
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"order-items1", OrderItem1ViewSet, basename="orderitem1")
router.register(r"order-items2", OrderItem2ViewSet, basename="orderitem2")
router.register(r"reports", ReportViewSet, basename="report")

urlpatterns = [
    path("", include(router.urls)),
]
