from django.db import models


class Source(models.Model):
    class SourceType(models.TextChoices):
        ECOURTS = 'ECOURTS', 'eCourts India Portal'
        SCI_PORTAL = 'SCI_PORTAL', 'Supreme Court of India Portal'
        HIGH_COURT_PORTAL = 'HIGH_COURT_PORTAL', 'High Court Portal'
        GAZETTE = 'GAZETTE', 'Official Gazette of India'
        PUBLIC_ARCHIVE = 'PUBLIC_ARCHIVE', 'Authorized Public Legal Archive'
        OTHER = 'OTHER', 'Other Verified Source'

    class ReliabilityStatus(models.TextChoices):
        OFFICIAL = 'OFFICIAL', 'Official Government / Judicial Portal'
        VERIFIED_PUBLIC = 'VERIFIED_PUBLIC', 'Verified Public Law Repository'
        UNVERIFIED = 'UNVERIFIED', 'Unverified External Document'

    source_name = models.CharField(max_length=150, help_text="e.g. eCourts India, SCI Portal")
    source_url = models.URLField(max_length=500, blank=True, null=True, help_text="Base URL of repository")
    source_type = models.CharField(
        max_length=30,
        choices=SourceType.choices,
        default=SourceType.ECOURTS
    )
    retrieved_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when data was initially retrieved")
    reliability_status = models.CharField(
        max_length=30,
        choices=ReliabilityStatus.choices,
        default=ReliabilityStatus.VERIFIED_PUBLIC
    )
    description = models.TextField(blank=True, null=True, help_text="Notes on data provenance and authenticity")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sources_source'
        ordering = ['-retrieved_at']

    def __str__(self):
        return f"{self.source_name} ({self.get_reliability_status_display()})"

