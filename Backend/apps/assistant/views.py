"""
NYAYASETU Assistant API Views

POST /api/assistant/
GET  /api/assistant/ (Information and endpoint guide)
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from apps.assistant.serializers import (
    AssistantQuerySerializer,
    AssistantResponseSerializer,
)
from apps.assistant.services import AssistantService
from apps.assistant.prompts import DISCLAIMER_TEXT


class AssistantChatView(APIView):
    """
    Evidence-grounded judicial assistant endpoint.
    Restricted to authenticated NYAYASETU citizens/users only.

    POST /api/assistant/
    Body:
    {
        "query": "What was the decision regarding equality under Article 14 in civil petitions?",
        "court_id": 1,         // optional
        "case_type": "Writ",   // optional
        "top_k": 5,            // optional
        "alpha": 0.5           // optional (keyword vs semantic balance)
    }
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            "service": "NYAYASETU AI Judicial Assistant",
            "description": "Evidence-oriented, citation-grounded legal information assistant.",
            "disclaimer": DISCLAIMER_TEXT,
            "method": "POST",
            "payload_example": {
                "query": "What relief was granted in employment benefit cases?",
                "top_k": 5,
                "alpha": 0.5,
                "court_id": None,
                "case_type": None,
                "year": None
            }
        })

    def post(self, request):
        serializer = AssistantQuerySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        filters = {}
        if data.get("court_id"):
            filters["court_id"] = data["court_id"]
        if data.get("case_type"):
            filters["case_type"] = data["case_type"]
        if data.get("year"):
            filters["year"] = data["year"]
        if data.get("document_type"):
            filters["document_type"] = data["document_type"]

        response_data = AssistantService.answer_question(
            query=data["query"],
            case_id=data.get("case_id"),
            filters=filters,
            top_k=data.get("top_k", 5),
            alpha=data.get("alpha", 0.5),
        )

        resp_serializer = AssistantResponseSerializer(response_data)
        return Response(resp_serializer.data, status=status.HTTP_200_OK)

