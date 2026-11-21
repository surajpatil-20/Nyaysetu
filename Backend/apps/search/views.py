"""
NYAYASETU Search API Views

GET /api/search/?q=<query>
GET /api/search/?q=<query>&court_id=1&case_type=Writ+Petition&year=2023&document_type=JUDGMENT
GET /api/search/cases/<id>/timeline/
"""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from apps.search.services import hybrid_search
from apps.search.serializers import EvidenceResultSerializer

logger = logging.getLogger(__name__)


class HybridSearchView(APIView):
    """
    Hybrid keyword + semantic search over judicial DocumentChunks.

    Query params:
        q           : search query (required)
        court_id    : filter by court ID
        case_type   : filter by case type string (icontains)
        year        : filter by year (filing or decision)
        document_type: filter by document type (JUDGMENT, FINAL_ORDER, etc.)
        top_k       : number of results (default 10, max 50)
        alpha       : keyword weight 0.0-1.0 (default 0.5)
    """
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response(
                {"error": "Query parameter 'q' is required.", "results": []},
                status=status.HTTP_400_BAD_REQUEST,
            )

        filters = {}
        if request.query_params.get("court_id"):
            try:
                filters["court_id"] = int(request.query_params["court_id"])
            except ValueError:
                pass
        if request.query_params.get("case_type"):
            filters["case_type"] = request.query_params["case_type"]
        if request.query_params.get("year"):
            try:
                filters["year"] = int(request.query_params["year"])
            except ValueError:
                pass
        if request.query_params.get("document_type"):
            filters["document_type"] = request.query_params["document_type"]

        try:
            top_k = min(int(request.query_params.get("top_k", 10)), 50)
        except ValueError:
            top_k = 10

        try:
            alpha = float(request.query_params.get("alpha", 0.5))
            alpha = max(0.0, min(1.0, alpha))
        except ValueError:
            alpha = 0.5

        group_by_case = request.query_params.get("group_by_case", "true").lower() in ("true", "1", "yes")

        try:
            results = hybrid_search(
                query,
                filters=filters,
                top_k=top_k,
                alpha=alpha,
                group_by_case=group_by_case,
            )
        except Exception as exc:
            logger.exception("Search failed for query '%s': %s", query, exc)
            return Response(
                {"error": "Search failed. Please try again.", "results": []},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        serializer = EvidenceResultSerializer(results, many=True)
        return Response({
            "query": query,
            "filters": filters,
            "count": len(results),
            "results": serializer.data,
        })


class CaseTimelineView(APIView):
    """
    GET /api/search/cases/<case_id>/timeline/

    Returns chronological case events for a case.
    """
    permission_classes = [AllowAny]

    def get(self, request, case_id):
        from apps.cases.models import Case, CaseEvent

        try:
            case = Case.objects.get(pk=case_id)
        except Case.DoesNotExist:
            return Response({"error": "Case not found."}, status=status.HTTP_404_NOT_FOUND)

        events = CaseEvent.objects.filter(case=case).order_by("event_date", "created_at")
        event_data = [
            {
                "event_id": ev.pk,
                "event_date": str(ev.event_date),
                "event_type": ev.event_type,
                "event_type_display": ev.get_event_type_display(),
                "title": ev.title,
                "description": ev.description,
                "document_id": ev.document_id,
                "source_url": ev.source_url,
            }
            for ev in events
        ]

        return Response({
            "case_id": case.pk,
            "case_number": case.case_number,
            "case_title": case.case_title,
            "timeline": event_data,
        })
