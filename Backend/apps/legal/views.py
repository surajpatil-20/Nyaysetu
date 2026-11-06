from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Act, Section, CaseSection
from .serializers import ActSerializer, SectionSerializer, CaseSectionSerializer


class ActViewSet(viewsets.ModelViewSet):
    queryset = Act.objects.prefetch_related('sections').all()
    serializer_class = ActSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['act_name', 'short_code', 'description']
    filterset_fields = ['act_year']
    ordering_fields = ['act_name', 'act_year']


class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.select_related('act').all()
    serializer_class = SectionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['section_number', 'title', 'description', 'act__act_name', 'act__short_code']
    filterset_fields = ['act', 'section_number']


class CaseSectionViewSet(viewsets.ModelViewSet):
    queryset = CaseSection.objects.select_related('case', 'section', 'section__act').all()
    serializer_class = CaseSectionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['case', 'section']

