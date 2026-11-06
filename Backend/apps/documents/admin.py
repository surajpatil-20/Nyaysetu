from django.contrib import admin
from .models import Document, DocumentChunk, UploadedDocument, UploadedDocumentChunk


class DocumentChunkInline(admin.TabularInline):
    model = DocumentChunk
    fields = ('chunk_index', 'page_number', 'token_count')
    readonly_fields = ('chunk_index', 'page_number', 'token_count')
    extra = 0
    can_delete = False


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'case', 'document_type', 'extraction_status', 'page_count', 'document_date')
    list_filter = ('document_type', 'extraction_status')
    search_fields = ('title', 'case__case_number')
    inlines = [DocumentChunkInline]


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'case', 'chunk_index', 'page_number', 'token_count')
    list_filter = ('page_number',)
    search_fields = ('content',)


@admin.register(UploadedDocument)
class UploadedDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'extraction_status', 'page_count', 'created_at')
    list_filter = ('extraction_status',)
    search_fields = ('title', 'user__username')

