from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Document, DocumentChunk, UploadedDocument, UploadedDocumentChunk
from .serializers import (
    DocumentSerializer, DocumentDetailSerializer,
    DocumentChunkSerializer, UploadedDocumentSerializer,
    UploadedDocumentChunkSerializer
)


class DocumentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['case', 'document_type', 'extraction_status', 'language', 'document_date']
    search_fields = ['title', 'case__case_number', 'extracted_text']
    ordering_fields = ['document_date', 'created_at']

    def get_queryset(self):
        qs = Document.objects.select_related('case')
        if self.action == 'list':
            include_demo = self.request.query_params.get('include_demo', '').lower() == 'true'
            if not include_demo:
                qs = qs.exclude(source_name='DEMO SOURCE').exclude(case__source_name='DEMO SOURCE')
            ordering = self.request.query_params.get('ordering', '')
            if not ordering or ordering == '-document_date':
                from django.db.models import F
                qs = qs.order_by(F('document_date').desc(nulls_last=True), '-created_at')
        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DocumentDetailSerializer
        return DocumentSerializer


class DocumentChunkViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DocumentChunk.objects.select_related('document', 'case').all()
    serializer_class = DocumentChunkSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['document', 'case', 'page_number']


class UploadedDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = UploadedDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Strict isolation: Citizen only sees their own uploaded records
        return UploadedDocument.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UploadedDocumentChunkViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UploadedDocumentChunkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Strict isolation: Only chunks owned by the logged in citizen
        return UploadedDocumentChunk.objects.filter(user=self.request.user)

