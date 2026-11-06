from django.db import models


class Court(models.Model):
    class CourtType(models.TextChoices):
        SUPREME_COURT = 'SUPREME_COURT', 'Supreme Court of India'
        HIGH_COURT = 'HIGH_COURT', 'High Court'
        DISTRICT_COURT = 'DISTRICT_COURT', 'District and Sessions Court'
        TRIBUNAL = 'TRIBUNAL', 'Judicial Tribunal / Commission'
        OTHER = 'OTHER', 'Other Subordinate Court'

    court_name = models.CharField(max_length=255, unique=True, help_text="e.g. Supreme Court of India, Delhi High Court")
    court_code = models.CharField(max_length=50, blank=True, null=True, unique=True, help_text="e.g. SCI, DELHC, BOMHC")
    court_type = models.CharField(
        max_length=30,
        choices=CourtType.choices,
        default=CourtType.OTHER
    )
    state = models.CharField(max_length=100, blank=True, null=True, help_text="State or UT jurisdiction")
    city = models.CharField(max_length=100, blank=True, null=True, help_text="Seat / bench location")
    address = models.TextField(blank=True, null=True)
    source_url = models.URLField(max_length=500, blank=True, null=True, help_text="Official court portal URL")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'courts_court'
        ordering = ['court_name']
        indexes = [
            models.Index(fields=['court_type'], name='court_type_idx'),
            models.Index(fields=['state'], name='court_state_idx'),
        ]

    def __str__(self):
        return f"{self.court_name} ({self.get_court_type_display()})"


class Judge(models.Model):
    name = models.CharField(max_length=255, help_text="e.g. Hon'ble Mr. Justice D. Y. Chandrachud")
    current_court = models.ForeignKey(
        Court,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sitting_judges',
        help_text="Current court of appointment"
    )
    designation = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Chief Justice of India, Chief Justice, Puisne Judge, etc."
    )
    source_url = models.URLField(max_length=500, blank=True, null=True, help_text="Public judicial profile or gazette link")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'courts_judge'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name'], name='judge_name_idx'),
        ]

    def __str__(self):
        return f"{self.name} - {self.designation or 'Judge'}"


class JudgeCourtHistory(models.Model):
    judge = models.ForeignKey(
        Judge,
        on_delete=models.CASCADE,
        related_name='court_history'
    )
    court = models.ForeignKey(
        Court,
        on_delete=models.CASCADE,
        related_name='judge_tenures'
    )
    designation = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'courts_judgecourthistory'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['judge', 'court'], name='judge_court_hist_idx'),
        ]

    def __str__(self):
        return f"{self.judge.name} at {self.court.court_name} ({self.start_date} to {self.end_date or 'Present'})"

