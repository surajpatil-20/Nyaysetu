from django.contrib import admin
from .models import Court, Judge, JudgeCourtHistory


class JudgeCourtHistoryInline(admin.TabularInline):
    model = JudgeCourtHistory
    extra = 1


@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ('court_name', 'court_code', 'court_type', 'state', 'city')
    list_filter = ('court_type', 'state')
    search_fields = ('court_name', 'court_code', 'city')


@admin.register(Judge)
class JudgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'designation', 'current_court')
    list_filter = ('designation', 'current_court')
    search_fields = ('name',)
    inlines = [JudgeCourtHistoryInline]

