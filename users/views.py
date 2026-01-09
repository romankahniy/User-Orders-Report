from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import User
from .serializers import UserSerializer, UserStatisticsSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['is_active', 'date_joined']
    search_fields = ['username', 'email']
    ordering_fields = ['date_joined', 'username', 'email']
    ordering = ['-date_joined']

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        queryset = self.filter_queryset(
            User.objects.with_statistics()
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserStatisticsSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UserStatisticsSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def user_statistics(self, request, pk=None):
        user = User.objects.with_statistics().get(pk=pk)
        serializer = UserStatisticsSerializer(user)
        return Response(serializer.data)
