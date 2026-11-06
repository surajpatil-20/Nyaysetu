"""
Search serializers for NYAYASETU.
"""
from rest_framework import serializers


class EvidenceResultSerializer(serializers.Serializer):
    chunk_id = serializers.IntegerField()
    case_id = serializers.IntegerField()
    case_number = serializers.CharField()
    case_title = serializers.CharField()
    document_id = serializers.IntegerField()
    document_title = serializers.CharField()
    document_type = serializers.CharField()
    page_number = serializers.IntegerField(allow_null=True)
    snippet = serializers.CharField()
    keyword_score = serializers.FloatField()
    semantic_score = serializers.FloatField()
    hybrid_score = serializers.FloatField()
    source_name = serializers.CharField(allow_null=True)
    source_url = serializers.CharField(allow_null=True)

