from django.contrib import admin
from .models import LawCategory, LawAct, LawSection, LegalScenario


@admin.register(LawCategory)
class LawCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'display_order', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    ordering = ('display_order', 'name')


@admin.register(LawAct)
class LawActAdmin(admin.ModelAdmin):
    list_display = ('act_name', 'short_code', 'act_year', 'official_url')
    search_fields = ('act_name', 'short_code', 'description')
    ordering = ('act_name',)


@admin.register(LawSection)
class LawSectionAdmin(admin.ModelAdmin):
    list_display = ('section_number', 'title', 'act', 'official_url')
    list_filter = ('act',)
    search_fields = ('section_number', 'title', 'legal_text', 'simple_explanation')
    ordering = ('act', 'section_number')


@admin.register(LegalScenario)
class LegalScenarioAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'helpline_number', 'is_featured', 'display_order')
    list_filter = ('category', 'is_featured')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'situation_summary', 'what_to_do')
    filter_horizontal = ('sections',)
    ordering = ('display_order', 'title')
