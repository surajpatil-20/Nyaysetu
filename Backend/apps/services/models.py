from django.db import models


class Service(models.Model):
    class ServiceCategory(models.TextChoices):
        LEGAL_AID = 'LEGAL_AID', 'Free Legal Aid (NALSA / SLSA / DLSA)'
        CASE_STATUS = 'CASE_STATUS', 'eCourts Case Status & Cause List'
        E_FILING = 'E_FILING', 'e-Filing Portal (High Courts & District Courts)'
        CERTIFIED_COPY = 'CERTIFIED_COPY', 'Certified Copy Application'
        CONSUMER_FORUM = 'CONSUMER_FORUM', 'e-Daakhil (Consumer Disputes)'
        TRAFFIC_CHALLAN = 'TRAFFIC_CHALLAN', 'Virtual Courts (Traffic & Petty Offences)'
        OTHER = 'OTHER', 'Other Official Judicial Service'

    service_name = models.CharField(max_length=255, help_text="e.g. NALSA Free Legal Services, eCourts Services Portal")
    category = models.CharField(
        max_length=50,
        choices=ServiceCategory.choices,
        default=ServiceCategory.OTHER
    )
    department = models.CharField(max_length=255, blank=True, null=True, help_text="e.g. National Legal Services Authority, Ministry of Law & Justice")
    state = models.CharField(max_length=100, blank=True, null=True, help_text="State jurisdiction (blank/null for All-India / Central)")
    description = models.TextField(help_text="Detailed guidance on how a citizen can access and utilize this service")
    eligibility = models.TextField(blank=True, null=True, help_text="Eligibility criteria (e.g. women, children, income limits under Section 12 Legal Services Authorities Act)")
    official_url = models.URLField(max_length=500, help_text="Verified direct official government/court portal URL")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'services_service'
        ordering = ['service_name']
        indexes = [
            models.Index(fields=['category'], name='service_category_idx'),
            models.Index(fields=['state'], name='service_state_idx'),
        ]

    def __str__(self):
        return f"{self.service_name} ({self.get_category_display()})"

