from django.contrib import admin
from .models import Source


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('source_name', 'source_type', 'reliability_status', 'retrieved_at')
    list_filter = ('source_type', 'reliability_status')
    search_fields = ('source_name', 'source_url')

