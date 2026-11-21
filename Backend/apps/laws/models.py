from django.db import models


class LawCategory(models.Model):
    name = models.CharField(max_length=200, unique=True, help_text="e.g. Consumer Rights & Online Fraud")
    slug = models.SlugField(max_length=200, unique=True, help_text="URL-friendly identifier")
    description = models.TextField(blank=True, help_text="Overview of legal rights and situations covered")
    icon = models.CharField(max_length=50, default="Scale", help_text="Lucide icon identifier name")
    display_order = models.IntegerField(default=0, help_text="Sort order for category listing")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'laws_category'
        ordering = ['display_order', 'name']
        verbose_name = 'Law Category'
        verbose_name_plural = 'Law Categories'

    def __str__(self):
        return self.name


class LawAct(models.Model):
    act_name = models.CharField(max_length=300, unique=True, help_text="Full official title, e.g. Consumer Protection Act, 2019")
    short_code = models.CharField(max_length=50, blank=True, null=True, help_text="Common abbreviation, e.g. CPA 2019, MVA 1988")
    act_year = models.IntegerField(blank=True, null=True, help_text="Year of enactment")
    enacted_by = models.CharField(max_length=200, default="Parliament of India", blank=True)
    description = models.TextField(blank=True, help_text="Official purpose, scope and preamble summary")
    official_url = models.URLField(max_length=500, help_text="Official verified India Code or Legislative portal URL")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'laws_act'
        ordering = ['act_name']
        verbose_name = 'Law Act'
        verbose_name_plural = 'Law Acts'

    def __str__(self):
        if self.short_code:
            return f"{self.act_name} ({self.short_code})"
        return self.act_name


class LawSection(models.Model):
    act = models.ForeignKey(LawAct, on_delete=models.CASCADE, related_name='sections', help_text="Enactment this section belongs to")
    section_number = models.CharField(max_length=50, help_text="e.g. Section 2(7), Section 35, Section 166")
    title = models.CharField(max_length=300, help_text="Section title / heading")
    legal_text = models.TextField(help_text="Verbatim / authoritative statutory text from India Code")
    simple_explanation = models.TextField(help_text="Plain-language explanation for citizens and non-lawyers")
    punishment_or_remedy = models.TextField(blank=True, null=True, help_text="Statutory remedies, damages, penalties, or compensation prescribed")
    official_url = models.URLField(max_length=500, help_text="Official verified link to India Code or government enactment")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'laws_section'
        ordering = ['section_number']
        constraints = [
            models.UniqueConstraint(fields=['act', 'section_number'], name='unique_act_section_number')
        ]
        indexes = [
            models.Index(fields=['act', 'section_number'], name='laws_sec_act_num_idx'),
        ]
        verbose_name = 'Law Section'
        verbose_name_plural = 'Law Sections'

    def __str__(self):
        return f"{self.act.short_code or self.act.act_name} - {self.section_number}: {self.title}"


class LegalScenario(models.Model):
    category = models.ForeignKey(LawCategory, on_delete=models.CASCADE, related_name='scenarios', help_text="Category of this real-life situation")
    title = models.CharField(max_length=300, help_text="Real-life situation title")
    slug = models.SlugField(max_length=300, unique=True, help_text="URL identifier")
    situation_summary = models.TextField(help_text="Detailed scenario description of what happens in daily life")
    what_to_do = models.TextField(help_text="Actionable, step-by-step guidance on how the citizen should handle the situation")
    sections = models.ManyToManyField(LawSection, related_name='scenarios', blank=True, help_text="Relevant statutory provisions")
    related_cases = models.ManyToManyField(
        'cases.Case',
        related_name='scenarios',
        blank=True,
        help_text="Authentic Supreme Court precedent cases linked to this scenario"
    )
    official_portal_url = models.URLField(max_length=500, blank=True, null=True, help_text="Direct link to government grievance, e-filing or tribunal portal")
    helpline_number = models.CharField(max_length=100, blank=True, null=True, help_text="Official citizen helpline (e.g. 1915, 1930, 181)")
    is_featured = models.BooleanField(default=False, help_text="Feature this scenario on homepage or highlights")
    display_order = models.IntegerField(default=0, help_text="Display priority order")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'laws_scenario'
        ordering = ['display_order', 'title']
        indexes = [
            models.Index(fields=['category'], name='laws_scen_cat_idx'),
            models.Index(fields=['slug'], name='laws_scen_slug_idx'),
        ]
        verbose_name = 'Legal Scenario'
        verbose_name_plural = 'Legal Scenarios'

    def __str__(self):
        return self.title
