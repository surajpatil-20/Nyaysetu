from rest_framework import serializers
from .models import Document, DocumentChunk, UploadedDocument, UploadedDocumentChunk


class DocumentChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentChunk
        fields = ['id', 'document', 'case', 'chunk_index', 'content', 'page_number', 'section_title', 'token_count', 'created_at']
        # embedding omitted from default JSON payload for performance and bandwidth


class DocumentSerializer(serializers.ModelSerializer):
    case_number = serializers.CharField(source='case.case_number', read_only=True)
    chunks_count = serializers.IntegerField(source='chunks.count', read_only=True)

    class Meta:
        model = Document
        fields = [
            'id', 'case', 'case_number', 'document_type',
            'title', 'file', 'source_url', 'source_name',
            'document_date', 'language', 'extraction_status',
            'page_count', 'chunks_count', 'created_at', 'updated_at'
        ]


class DocumentDetailSerializer(serializers.ModelSerializer):
    case_number = serializers.CharField(source='case.case_number', read_only=True)
    chunks = DocumentChunkSerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = '__all__'


class UploadedDocumentChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedDocumentChunk
        fields = ['id', 'uploaded_document', 'chunk_index', 'content', 'page_number', 'created_at']


class UploadedDocumentSerializer(serializers.ModelSerializer):
    chunks_count = serializers.IntegerField(source='chunks.count', read_only=True)

    class Meta:
        model = UploadedDocument
        fields = [
            'id', 'title', 'file', 'extraction_status',
            'page_count', 'is_private', 'chunks_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'extraction_status', 'page_count', 'is_private', 'chunks_count', 'created_at', 'updated_at']

