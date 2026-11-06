"""
Serializers for NYAYASETU Assistant API.
"""
from rest_framework import serializers


class SourceCitationSerializer(serializers.Serializer):
    citation_tag = serializers.CharField()
    chunk_id = serializers.IntegerField()
    case_id = serializers.IntegerField()
    case_number = serializers.CharField()
    case_title = serializers.CharField()
    document_id = serializers.IntegerField()
    document_title = serializers.CharField()
    document_type = serializers.CharField()
    page_number = serializers.IntegerField(allow_null=True)
    snippet = serializers.CharField()
    relevance_score = serializers.FloatField()
    source_name = serializers.CharField(allow_null=True)
    source_url = serializers.CharField(allow_null=True)


class AssistantQuerySerializer(serializers.Serializer):
    query = serializers.CharField(
        max_length=1000,
        required=True,
        help_text="User legal question or topic to research"
    )
    court_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Optional filter for specific court ID"
    )
    case_type = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text="Optional case type filter, e.g. Writ Petition"
    )
    year = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Optional year filter"
    )
    document_type = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        help_text="Optional document type filter, e.g. JUDGMENT"
    )
    top_k = serializers.IntegerField(
        default=5,
        min_value=1,
        max_value=20,
        help_text="Number of evidence chunks to retrieve (1-20)"
    )
    alpha = serializers.FloatField(
        default=0.5,
        min_value=0.0,
        max_value=1.0,
        help_text="Hybrid search weighting: 1.0 = keyword only, 0.0 = semantic only, 0.5 = balanced"
    )


class AssistantResponseSerializer(serializers.Serializer):
    query = serializers.CharField()
    answer = serializers.CharField()
    has_sufficient_evidence = serializers.BooleanField()
    evidence_count = serializers.IntegerField()
    sources = SourceCitationSerializer(many=True)
    disclaimer = serializers.CharField()

