from rest_framework import serializers
from .models import Act, Section, CaseSection


class SectionSerializer(serializers.ModelSerializer):
    act_name = serializers.CharField(source='act.act_name', read_only=True)
    short_code = serializers.CharField(source='act.short_code', read_only=True)

    class Meta:
        model = Section
        fields = ['id', 'act', 'act_name', 'short_code', 'section_number', 'title', 'description', 'source_url', 'created_at']


class ActSerializer(serializers.ModelSerializer):
    sections_count = serializers.IntegerField(source='sections.count', read_only=True)

    class Meta:
        model = Act
        fields = ['id', 'act_name', 'act_year', 'short_code', 'description', 'source_url', 'sections_count', 'created_at']


class CaseSectionSerializer(serializers.ModelSerializer):
    section_detail = SectionSerializer(source='section', read_only=True)

    class Meta:
        model = CaseSection
        fields = ['id', 'case', 'section', 'section_detail', 'reference_context', 'created_at']

