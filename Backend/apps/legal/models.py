from django.db import models


class Act(models.Model):
    act_name = models.CharField(max_length=300, help_text="e.g. Indian Penal Code, Code of Criminal Procedure")
    act_year = models.IntegerField(blank=True, null=True, help_text="Year of enactment, e.g. 1860")
    short_code = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. IPC, CrPC, CPC, BNS")
    description = models.TextField(blank=True, null=True, help_text="Statute summary and scope")
    source_url = models.URLField(max_length=500, blank=True, null=True, help_text="Official India Code link")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'legal_act'
        ordering = ['act_name']
        constraints = [
            models.UniqueConstraint(fields=['act_name', 'act_year'], name='unique_act_name_year')
        ]
        indexes = [
            models.Index(fields=['act_name'], name='act_name_idx'),
            models.Index(fields=['short_code'], name='act_short_code_idx'),
        ]

    def __str__(self):
        if self.act_year:
            return f"{self.act_name} ({self.act_year})"
        return self.act_name


class Section(models.Model):
    act = models.ForeignKey(
        Act,
        on_delete=models.CASCADE,
        related_name='sections',
        help_text="Parent Act"
    )
    section_number = models.CharField(max_length=50, help_text="e.g. 302, 420, 438(1), 21")
    title = models.CharField(max_length=300, blank=True, null=True, help_text="Section title / caption")
    description = models.TextField(blank=True, null=True, help_text="Official statutory text of this section")
    source_url = models.URLField(max_length=500, blank=True, null=True, help_text="Official section link")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'legal_section'
        ordering = ['section_number']
        constraints = [
            models.UniqueConstraint(fields=['act', 'section_number'], name='unique_section_act_number')
        ]
        indexes = [
            models.Index(fields=['act', 'section_number'], name='section_act_num_idx'),
        ]

    def __str__(self):
        return f"{self.act.short_code or self.act.act_name} - Section {self.section_number}"


class CaseSection(models.Model):
    case = models.ForeignKey(
        'cases.Case',
        on_delete=models.CASCADE,
        related_name='case_sections',
        help_text="Case referring to this section"
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='case_references',
        help_text="Section referenced"
    )
    reference_context = models.TextField(
        blank=True,
        null=True,
        help_text="Contextual excerpt from judgment/order where section is invoked"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'legal_casesection'
        constraints = [
            models.UniqueConstraint(fields=['case', 'section'], name='unique_case_section')
        ]
        indexes = [
            models.Index(fields=['case', 'section'], name='case_sec_idx'),
        ]

    def __str__(self):
        return f"Case #{self.case_id} refers to {self.section}"
