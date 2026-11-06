"""
API views for NYAYASETU Judicial Knowledge Graph.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .services import get_case_graph
from .sync import sync_knowledge_graph
from .connection import check_neo4j_connection


class CaseGraphView(APIView):
    """
    GET /api/graph/cases/<case_id>/
    Returns graph representation of a case (nodes, links, textual relationships).
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, case_id):
        graph_data = get_case_graph(case_id)
        if graph_data is None:
            return Response(
                {"error": f"Case with id {case_id} not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(graph_data, status=status.HTTP_200_OK)


class GraphStatusView(APIView):
    """
    GET /api/graph/status/
    Returns Neo4j connection status and configuration.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        connected, message = check_neo4j_connection()
        return Response({
            "neo4j_connected": connected,
            "status_message": message,
            "architecture": "PostgreSQL is Primary Source of Truth; Neo4j is Derived Knowledge Graph",
        })


class GraphSyncView(APIView):
    """
    POST /api/graph/sync/
    Trigger knowledge graph sync. Admin only.
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        dry_run = request.data.get("dry_run", False)
        case_id = request.data.get("case_id", None)
        stats = sync_knowledge_graph(dry_run=dry_run, case_id=case_id)
        return Response(stats, status=status.HTTP_200_OK)

