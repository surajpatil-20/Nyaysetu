from django.contrib import admin
from .models import Case, Party, CaseParty, CaseJudge, CaseEvent, CaseCitation


class CasePartyInline(admin.TabularInline):
    model = CaseParty
    extra = 1


class CaseJudgeInline(admin.TabularInline):
    model = CaseJudge
    extra = 1


class CaseEventInline(admin.TabularInline):
    model = CaseEvent
    extra = 1


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('case_number', 'case_title', 'court', 'decision_date', 'status')
    list_filter = ('status', 'court', 'case_type')
    search_fields = ('case_number', 'cnr_number', 'case_title')
    inlines = [CasePartyInline, CaseJudgeInline, CaseEventInline]


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ('name', 'party_type', 'created_at')
    search_fields = ('name',)
    list_filter = ('party_type',)


@admin.register(CaseCitation)
class CaseCitationAdmin(admin.ModelAdmin):
    list_display = ('source_case', 'citation_text', 'cited_case', 'created_at')
    search_fields = ('citation_text',)

