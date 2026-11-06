from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from pgvector.django import VectorField, HnswIndex


class Document(models.Model):
    class DocumentType(models.TextChoices):
        JUDGMENT = 'JUDGMENT', 'Final Judgment'
        FINAL_ORDER = 'FINAL_ORDER', 'Final Order'
        INTERIM_ORDER = 'INTERIM_ORDER', 'Interim / Procedural Order'
        PETITION = 'PETITION', 'Petition / Appeal Paperbook'
        AFFIDAVIT = 'AFFIDAVIT', 'Affidavit / Counter-Affidavit'
        OTHER = 'OTHER', 'Other Judicial Record'

    class ExtractionStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending Extraction'
        COMPLETED = 'COMPLETED', 'Extraction Completed'
        FAILED = 'FAILED', 'Extraction Failed'
        OCR_REQUIRED = 'OCR_REQUIRED', 'Scanned Document (OCR Required)'

    case = models.ForeignKey(
        'cases.Case',
        on_delete=models.CASCADE,
        related_name='documents',
        help_text="Associated case"
    )
    document_type = models.CharField(
        max_length=30,
        choices=DocumentType.choices,
        default=DocumentType.JUDGMENT
    )
    title = models.CharField(max_length=300, help_text="e.g. Final Judgment in W.P. 1234/2023")
    file = models.FileField(
        upload_to='judicial_documents/%Y/%m/',
        blank=True,
        null=True,
        help_text="Stored PDF file"
    )
    source_url = models.URLField(max_length=500, blank=True, null=True, help_text="Public PDF source link")
    source_name = models.CharField(max_length=150, blank=True, null=True, help_text="Source repository caption")
    document_date = models.DateField(blank=True, null=True, help_text="Date of order / judgment")
    language = models.CharField(max_length=20, default='en', help_text="Primary language (ISO code)")
    extracted_text = models.TextField(blank=True, null=True, help_text="Full text parsed from document")
    extraction_status = models.CharField(
        max_length=20,
        choices=ExtractionStatus.choices,
        default=ExtractionStatus.PENDING
    )
    page_count = models.IntegerField(blank=True, null=True, help_text="Total pages")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'documents_document'
        ordering = ['-document_date', '-created_at']
        indexes = [
            models.Index(fields=['case', 'document_type'], name='doc_case_type_idx'),
            models.Index(fields=['document_date'], name='doc_date_idx'),
            models.Index(fields=['extraction_status'], name='doc_extract_status_idx'),
        ]

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.title} ({self.case.case_number})"


class DocumentChunk(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='chunks',
        help_text="Parent document"
    )
    case = models.ForeignKey(
        'cases.Case',
        on_delete=models.CASCADE,
        related_name='document_chunks',
        help_text="Denormalized case reference for fast filtering"
    )
    chunk_index = models.IntegerField(help_text="Sequential chunk order index within document")
    content = models.TextField(help_text="Chunk text content for semantic retrieval")
    page_number = models.IntegerField(blank=True, null=True, help_text="PDF page number for grounded citation")
    section_title = models.CharField(max_length=255, blank=True, null=True, help_text="Contextual heading if extracted")
    token_count = models.IntegerField(blank=True, null=True, help_text="Approximate token count")
    # Fixed 768-dimensional dense vector (pgvector VectorField)
    embedding = VectorField(
        dimensions=768,
        blank=True,
        null=True,
        help_text="Fixed 768-dimensional dense vector"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'documents_documentchunk'
        ordering = ['document', 'chunk_index']
        constraints = [
            models.UniqueConstraint(fields=['document', 'chunk_index'], name='unique_document_chunk_index')
        ]
        indexes = [
            models.Index(fields=['case'], name='chunk_case_idx'),
            HnswIndex(
                name='doc_chunk_embed_hnsw_idx',
                fields=['embedding'],
                m=16,
                ef_construction=64,
                opclasses=['vector_cosine_ops'],
            ),
        ]

    def __str__(self):
        return f"Chunk {self.chunk_index} of Doc #{self.document_id} (Page {self.page_number or '?'})"


class UploadedDocument(models.Model):
    class ExtractionStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending Extraction'
        COMPLETED = 'COMPLETED', 'Extraction Completed'
        FAILED = 'FAILED', 'Extraction Failed'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_documents',
        help_text="Owner user - strict privacy enforcement"
    )
    title = models.CharField(max_length=255, help_text="User title or original filename")
    file = models.FileField(
        upload_to='user_uploads/%Y/%m/',
        help_text="Private user uploaded file"
    )
    extracted_text = models.TextField(blank=True, null=True)
    extraction_status = models.CharField(
        max_length=20,
        choices=ExtractionStatus.choices,
        default=ExtractionStatus.PENDING
    )
    page_count = models.IntegerField(blank=True, null=True)
    is_private = models.BooleanField(default=True, help_text="Private to the owning user")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'documents_uploadeddocument'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at'], name='user_upload_idx'),
        ]

    def __str__(self):
        return f"{self.title} (User #{self.user_id})"


class UploadedDocumentChunk(models.Model):
    uploaded_document = models.ForeignKey(
        UploadedDocument,
        on_delete=models.CASCADE,
        related_name='chunks',
        help_text="Parent user-uploaded document"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_chunks',
        help_text="Denormalized user reference for tenant isolation"
    )
    chunk_index = models.IntegerField(help_text="Sequential index within document")
    content = models.TextField(help_text="Chunk text")
    page_number = models.IntegerField(blank=True, null=True)
    # Fixed 768-dimensional dense vector (pgvector VectorField)
    embedding = VectorField(
        dimensions=768,
        blank=True,
        null=True,
        help_text="Fixed 768-dimensional dense vector"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'documents_uploadeddocumentchunk'
        ordering = ['uploaded_document', 'chunk_index']
        constraints = [
            models.UniqueConstraint(fields=['uploaded_document', 'chunk_index'], name='unique_uploaded_document_chunk_index')
        ]
        indexes = [
            models.Index(fields=['user'], name='upload_chunk_user_idx'),
            HnswIndex(
                name='up_chunk_embed_hnsw_idx',
                fields=['embedding'],
                m=16,
                ef_construction=64,
                opclasses=['vector_cosine_ops'],
            ),
        ]

    def clean(self):
        super().clean()
        if self.uploaded_document and self.user_id != self.uploaded_document.user_id:
            raise ValidationError("UploadedDocumentChunk user must match the parent UploadedDocument owner.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"User Chunk {self.chunk_index} of Upload #{self.uploaded_document_id}"
