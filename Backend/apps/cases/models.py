from django.db import models
from django.contrib.postgres.search import SearchVectorField


class Party(models.Model):
    class PartyType(models.TextChoices):
        INDIVIDUAL = 'INDIVIDUAL', 'Individual Person'
        STATE = 'STATE', 'State / Government Body'
        CORPORATION = 'CORPORATION', 'Private Corporation / Entity'
        ORGANIZATION = 'ORGANIZATION', 'Non-Governmental Organization / Trust'
        OTHER = 'OTHER', 'Other / Unspecified'

    name = models.CharField(max_length=300, help_text="e.g. State of Maharashtra, Ramesh Kumar")
    party_type = models.CharField(
        max_length=30,
        choices=PartyType.choices,
        blank=True,
        null=True,
        default=PartyType.OTHER
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cases_party'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name'], name='party_name_idx'),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_party_type_display() or 'Party'})"


class Case(models.Model):
    class CaseStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending Hearing / Decision'
        DISPOSED = 'DISPOSED', 'Disposed / Final Judgment Pronounced'
        WITHDRAWN = 'WITHDRAWN', 'Withdrawn by Petitioner'
        TRANSFERRED = 'TRANSFERRED', 'Transferred to Another Bench / Court'
        OTHER = 'OTHER', 'Other Procedural State'
        UNKNOWN = 'UNKNOWN', 'Status Unknown / Not Reported'

    case_number = models.CharField(
        max_length=100,
        help_text="Official docket number, e.g. W.P.(C) 1234/2023, Crl.A. 456/2021"
    )
    cnr_number = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        unique=True,
        help_text="16-character Case National Identifier (CNR) from eCourts"
    )
    case_title = models.CharField(
        max_length=500,
        help_text="Formal caption, e.g. State of Maharashtra v. ABC Corp"
    )
    case_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="e.g. Writ Petition, Special Leave Petition, Criminal Appeal"
    )
    court = models.ForeignKey(
        'courts.Court',
        on_delete=models.PROTECT,
        related_name='cases',
        help_text="Court adjudicating this case"
    )
    source = models.ForeignKey(
        'sources.Source',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cases',
        help_text="Provenance source"
    )
    filing_date = models.DateField(blank=True, null=True)
    registration_date = models.DateField(blank=True, null=True)
    decision_date = models.DateField(blank=True, null=True, help_text="Disposal / Judgment date")
    status = models.CharField(
        max_length=20,
        choices=CaseStatus.choices,
        default=CaseStatus.UNKNOWN
    )
    description = models.TextField(blank=True, null=True, help_text="Brief procedural or factual summary")
    source_url = models.URLField(max_length=500, blank=True, null=True, help_text="Original public source URL")
    source_name = models.CharField(max_length=150, blank=True, null=True, help_text="Source repository caption")
    search_vector = SearchVectorField(
        blank=True,
        null=True,
        help_text="Prepared PostgreSQL full-text search vector"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cases_case'
        ordering = ['-decision_date', '-filing_date', '-created_at']
        indexes = [
            models.Index(fields=['case_number'], name='case_number_idx'),
            models.Index(fields=['cnr_number'], name='case_cnr_idx'),
            models.Index(fields=['court', 'status'], name='case_court_status_idx'),
            models.Index(fields=['decision_date'], name='case_decision_date_idx'),
            models.Index(fields=['status'], name='case_status_idx'),
        ]

    def __str__(self):
        return f"{self.case_number} - {self.case_title}"


class CaseParty(models.Model):
    class PartyRole(models.TextChoices):
        PETITIONER = 'PETITIONER', 'Petitioner'
        RESPONDENT = 'RESPONDENT', 'Respondent'
        APPELLANT = 'APPELLANT', 'Appellant'
        RESPONDENT_APPELLANT = 'RESPONDENT_APPELLANT', 'Respondent / Cross-Appellant'
        INTERVENER = 'INTERVENER', 'Intervener / Amicus Curiae'
        OTHER = 'OTHER', 'Other Party'

    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='case_parties'
    )
    party = models.ForeignKey(
        Party,
        on_delete=models.CASCADE,
        related_name='party_cases'
    )
    role = models.CharField(
        max_length=30,
        choices=PartyRole.choices,
        default=PartyRole.PETITIONER
    )
    party_order = models.IntegerField(default=1, help_text="Ordering rank among parties (e.g. 1st Respondent)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cases_caseparty'
        ordering = ['party_order']
        constraints = [
            models.UniqueConstraint(fields=['case', 'party', 'role'], name='unique_case_party_role')
        ]
        indexes = [
            models.Index(fields=['case', 'role'], name='caseparty_role_idx'),
        ]

    def __str__(self):
        return f"{self.party.name} ({self.get_role_display()}) in {self.case.case_number}"


class CaseJudge(models.Model):
    class JudgeRole(models.TextChoices):
        PRESIDING = 'PRESIDING', 'Presiding / Senior Judge'
        MEMBER = 'MEMBER', 'Bench Member'
        CONCURRING = 'CONCURRING', 'Concurring Opinion'
        DISSENTING = 'DISSENTING', 'Dissenting Opinion'
        OTHER = 'OTHER', 'Other Role'

    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='case_judges'
    )
    judge = models.ForeignKey(
        'courts.Judge',
        on_delete=models.PROTECT,
        related_name='judge_cases'
    )
    role = models.CharField(
        max_length=30,
        choices=JudgeRole.choices,
        default=JudgeRole.MEMBER
    )
    bench_order = models.IntegerField(default=1, help_text="Bench position / precedence rank")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cases_casejudge'
        ordering = ['bench_order']
        constraints = [
            models.UniqueConstraint(fields=['case', 'judge'], name='unique_case_judge')
        ]
        indexes = [
            models.Index(fields=['case', 'judge'], name='case_judge_idx'),
        ]

    def __str__(self):
        return f"{self.judge.name} ({self.get_role_display()}) on {self.case.case_number}"


class CaseEvent(models.Model):
    class EventType(models.TextChoices):
        FILED = 'FILED', 'Case Filed'
        REGISTRATION = 'REGISTRATION', 'Registry Registered'
        HEARING = 'HEARING', 'Hearing / Proceeding'
        ORDER = 'ORDER', 'Interim Order Passed'
        JUDGMENT = 'JUDGMENT', 'Final Judgment Pronounced'
        ADJOURNMENT = 'ADJOURNMENT', 'Adjournment'
        OTHER = 'OTHER', 'Other Procedural Event'

    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='timeline_events'
    )
    event_date = models.DateField(help_text="Date the event took place")
    event_type = models.CharField(
        max_length=30,
        choices=EventType.choices,
        default=EventType.HEARING
    )
    title = models.CharField(max_length=255, help_text="Short event title")
    description = models.TextField(blank=True, null=True, help_text="Proceedings description or judicial note")
    document = models.ForeignKey(
        'documents.Document',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='event_records',
        help_text="Associated order or record if available"
    )
    source_url = models.URLField(max_length=500, blank=True, null=True, help_text="Direct link verifying event")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cases_caseevent'
        ordering = ['event_date', 'created_at']
        indexes = [
            models.Index(fields=['case', 'event_date'], name='case_event_date_idx'),
        ]

    def __str__(self):
        return f"{self.event_date} - {self.title} ({self.case.case_number})"


class CaseCitation(models.Model):
    source_case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='citations_made',
        help_text="The case that cites a precedent"
    )
    cited_case = models.ForeignKey(
        Case,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='citations_received',
        help_text="The cited precedent case (if present in NYAYASETU dataset)"
    )
    citation_text = models.CharField(
        max_length=300,
        help_text="Official citation string, e.g. (1973) 4 SCC 225, AIR 1967 SC 1643"
    )
    source_document = models.ForeignKey(
        'documents.Document',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contained_citations',
        help_text="The specific judgment/order containing this citation"
    )
    page_number = models.IntegerField(blank=True, null=True, help_text="Page number in judgment")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cases_casecitation'
        ordering = ['created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['source_case', 'cited_case', 'citation_text'],
                name='unique_case_citation'
            )
        ]
        indexes = [
            models.Index(fields=['citation_text'], name='citation_text_idx'),
            models.Index(fields=['source_case'], name='citation_src_idx'),
            models.Index(fields=['cited_case'], name='citation_cited_idx'),
        ]

    def __str__(self):
        return f"{self.source_case.case_number} cites {self.citation_text}"
