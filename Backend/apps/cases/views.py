from rest_framework import viewsets, permissions, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Case, Party, CaseParty, CaseJudge, CaseEvent, CaseCitation
from .serializers import (
    CaseListSerializer, CaseDetailSerializer,
    PartySerializer, CasePartySerializer,
    CaseJudgeSerializer, CaseEventSerializer,
    CaseCitationSerializer
)


class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.select_related('court', 'source').all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['court', 'status', 'case_type', 'decision_date', 'filing_date']
    search_fields = ['case_number', 'cnr_number', 'case_title', 'description']
    ordering_fields = ['decision_date', 'filing_date', 'created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CaseDetailSerializer
        return CaseListSerializer


class PartyViewSet(viewsets.ModelViewSet):
    queryset = Party.objects.all()
    serializer_class = PartySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    filterset_fields = ['party_type']


class CasePartyViewSet(viewsets.ModelViewSet):
    queryset = CaseParty.objects.select_related('case', 'party').all()
    serializer_class = CasePartySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['case', 'party', 'role']


class CaseJudgeViewSet(viewsets.ModelViewSet):
    queryset = CaseJudge.objects.select_related('case', 'judge').all()
    serializer_class = CaseJudgeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['case', 'judge', 'role']


class CaseEventViewSet(viewsets.ModelViewSet):
    queryset = CaseEvent.objects.select_related('case', 'document').all()
    serializer_class = CaseEventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['case', 'event_type', 'event_date']
    ordering_fields = ['event_date']


class CaseCitationViewSet(viewsets.ModelViewSet):
    queryset = CaseCitation.objects.select_related('source_case', 'cited_case', 'source_document').all()
    serializer_class = CaseCitationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['source_case', 'cited_case']
    search_fields = ['citation_text']


class RelatedCasesView(APIView):
    """
    GET /api/cases/<case_id>/related/
    Returns related cases via citations, shared judges, or shared court.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, case_id):
        try:
            case = Case.objects.get(pk=case_id)
        except Case.DoesNotExist:
            return Response({"error": "Case not found."}, status=status.HTTP_404_NOT_FOUND)

        related = []

        # 1. Cases this case cites
        for citation in CaseCitation.objects.filter(source_case=case, cited_case__isnull=False).select_related('cited_case', 'cited_case__court')[:10]:
            c = citation.cited_case
            related.append({
                "id": c.pk,
                "case_number": c.case_number,
                "case_title": c.case_title,
                "decision_date": str(c.decision_date) if c.decision_date else None,
                "status": c.status,
                "court_name": c.court.court_name if c.court else None,
                "relationship_type": "CITES",
                "reason": f"Directly cited as precedent ({citation.citation_text})",
            })

        # 2. Cases that cite this case
        for citation in CaseCitation.objects.filter(cited_case=case).select_related('source_case', 'source_case__court')[:10]:
            c = citation.source_case
            related.append({
                "id": c.pk,
                "case_number": c.case_number,
                "case_title": c.case_title,
                "decision_date": str(c.decision_date) if c.decision_date else None,
                "status": c.status,
                "court_name": c.court.court_name if c.court else None,
                "relationship_type": "CITED_BY",
                "reason": f"Cited by this case in judgment ({citation.citation_text})",
            })

        # 3. Cases heard by the same judges
        judge_ids = CaseJudge.objects.filter(case=case).values_list('judge_id', flat=True)
        if judge_ids:
            same_judge_cases = Case.objects.filter(
                case_judges__judge_id__in=judge_ids
            ).exclude(pk=case.pk).select_related('court').distinct()[:5]
            for c in same_judge_cases:
                related.append({
                    "id": c.pk,
                    "case_number": c.case_number,
                    "case_title": c.case_title,
                    "decision_date": str(c.decision_date) if c.decision_date else None,
                    "status": c.status,
                    "court_name": c.court.court_name if c.court else None,
                    "relationship_type": "SHARED_BENCH",
                    "reason": "Adjudicated by the same bench or judge",
                })

        # Deduplicate
        seen = set()
        unique_related = []
        for item in related:
            if item["id"] not in seen:
                seen.add(item["id"])
                unique_related.append(item)

        return Response({
            "case_id": case.pk,
            "case_number": case.case_number,
            "related_cases": unique_related[:20],
        })


class AdminStatsView(APIView):
    """
    GET /api/admin/stats/
    Platform statistics. Admin only.
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        from apps.documents.models import Document, DocumentChunk, UploadedDocument
        from apps.courts.models import Court, Judge
        from django.contrib.auth import get_user_model

        User = get_user_model()
        return Response({
            "cases": Case.objects.count(),
            "courts": Court.objects.count(),
            "judges": Judge.objects.count(),
            "parties": Party.objects.count(),
            "documents": Document.objects.count(),
            "document_chunks": DocumentChunk.objects.count(),
            "uploaded_documents": UploadedDocument.objects.count(),
            "users": User.objects.count(),
        })
