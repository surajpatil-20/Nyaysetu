from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from .models import LawCategory, LawAct, LawSection, LegalScenario
from .serializers import (
    LawCategorySerializer,
    LawActSerializer,
    LawSectionSerializer,
    LegalScenarioListSerializer,
    LegalScenarioDetailSerializer,
)


class LawCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API for browsing broad legal categories of citizen rights.
    """
    queryset = LawCategory.objects.annotate(
        scenario_count_annotated=Count('scenarios')
    ).order_by('display_order', 'name')
    serializer_class = LawCategorySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    pagination_class = None  # Return all categories cleanly for pills/cards


class LawActViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API for authoritative Indian statutory Acts.
    """
    queryset = LawAct.objects.all().order_by('act_name')
    serializer_class = LawActSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['act_name', 'short_code', 'description']


class LawSectionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API for statutory sections with citizen explanations and official sources.
    """
    queryset = LawSection.objects.select_related('act').all().order_by('act__act_name', 'section_number')
    serializer_class = LawSectionSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['act', 'act__short_code']
    search_fields = ['section_number', 'title', 'simple_explanation', 'legal_text']


class LegalScenarioViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API for real-life legal situations, applicable sections, citizen guidance and official sources.
    """
    queryset = LegalScenario.objects.select_related('category').prefetch_related(
        'sections__act'
    ).all().order_by('display_order', 'id')
    permission_classes = [permissions.AllowAny]
    pagination_class = None  # Return all scenarios cleanly for client-side filtering and counting
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'category__slug', 'is_featured']
    search_fields = [
        'title',
        'situation_summary',
        'what_to_do',
        'sections__title',
        'sections__section_number',
        'sections__act__act_name',
        'sections__act__short_code',
    ]
    ordering_fields = ['display_order', 'created_at', 'title']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LegalScenarioDetailSerializer
        return LegalScenarioListSerializer

    @action(detail=True, methods=['get'], url_path='related-cases')
    def related_cases(self, request, pk=None):
        """
        GET /api/laws/scenarios/<id>/related-cases/
        Returns 5-8 ranked, genuinely relevant authentic Supreme Court cases.
        """
        scenario = self.get_object()
        from .services import get_scenario_related_cases
        from .serializers import ScenarioRelatedCaseSerializer
        cases = get_scenario_related_cases(scenario)
        serializer = ScenarioRelatedCaseSerializer(cases, many=True)
        return Response({
            "scenario_id": scenario.id,
            "scenario_title": scenario.title,
            "count": len(cases),
            "related_cases": serializer.data
        })
