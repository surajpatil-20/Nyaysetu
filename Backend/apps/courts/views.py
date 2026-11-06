from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Court, Judge, JudgeCourtHistory
from .serializers import CourtSerializer, JudgeSerializer, JudgeCourtHistorySerializer


class CourtViewSet(viewsets.ModelViewSet):
    queryset = Court.objects.all()
    serializer_class = CourtSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['court_type', 'state', 'city']
    search_fields = ['court_name', 'court_code', 'city', 'state']
    ordering_fields = ['court_name', 'created_at']


class JudgeViewSet(viewsets.ModelViewSet):
    queryset = Judge.objects.select_related('current_court').prefetch_related('court_history').all()
    serializer_class = JudgeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['current_court', 'designation']
    search_fields = ['name', 'designation']


class JudgeCourtHistoryViewSet(viewsets.ModelViewSet):
    queryset = JudgeCourtHistory.objects.select_related('judge', 'court').all()
    serializer_class = JudgeCourtHistorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['judge', 'court']

