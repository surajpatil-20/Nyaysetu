from django.contrib import admin
from .models import Act, Section, CaseSection


class SectionInline(admin.TabularInline):
    model = Section
    extra = 1


@admin.register(Act)
class ActAdmin(admin.ModelAdmin):
    list_display = ('act_name', 'act_year', 'short_code')
    search_fields = ('act_name', 'short_code')
    inlines = [SectionInline]


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('section_number', 'act', 'title')
    list_filter = ('act',)
    search_fields = ('section_number', 'title', 'act__act_name')


@admin.register(CaseSection)
class CaseSectionAdmin(admin.ModelAdmin):
    list_display = ('case', 'section', 'created_at')
    search_fields = ('case__case_number', 'section__section_number')

