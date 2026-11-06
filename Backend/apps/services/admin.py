from django.contrib import admin
from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service_name', 'category', 'department', 'state', 'official_url')
    list_filter = ('category', 'state')
    search_fields = ('service_name', 'department', 'description')

