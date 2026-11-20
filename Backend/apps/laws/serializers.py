from rest_framework import serializers
from .models import LawCategory, LawAct, LawSection, LegalScenario


class LawActSerializer(serializers.ModelSerializer):
    class Meta:
        model = LawAct
        fields = [
            'id',
            'act_name',
            'short_code',
            'act_year',
            'enacted_by',
            'description',
            'official_url',
        ]


class LawSectionSerializer(serializers.ModelSerializer):
    act = LawActSerializer(read_only=True)
    act_id = serializers.PrimaryKeyRelatedField(
        queryset=LawAct.objects.all(), source='act', write_only=True, required=False
    )

    class Meta:
        model = LawSection
        fields = [
            'id',
            'act',
            'act_id',
            'section_number',
            'title',
            'legal_text',
            'simple_explanation',
            'punishment_or_remedy',
            'official_url',
        ]


class LawCategorySerializer(serializers.ModelSerializer):
    scenario_count = serializers.SerializerMethodField()

    class Meta:
        model = LawCategory
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'icon',
            'display_order',
            'scenario_count',
        ]

    def get_scenario_count(self, obj):
        if hasattr(obj, 'scenario_count_annotated'):
            return obj.scenario_count_annotated
        return obj.scenarios.count()


class LegalScenarioListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    sections_count = serializers.SerializerMethodField()
    act_tags = serializers.SerializerMethodField()

    class Meta:
        model = LegalScenario
        fields = [
            'id',
            'title',
            'slug',
            'category',
            'category_name',
            'category_slug',
            'situation_summary',
            'helpline_number',
            'official_portal_url',
            'is_featured',
            'display_order',
            'sections_count',
            'act_tags',
        ]

    def get_sections_count(self, obj):
        return obj.sections.count()

    def get_act_tags(self, obj):
        # Extract unique short codes or act names of sections linked
        tags = []
        for s in obj.sections.select_related('act').all():
            label = f"{s.act.short_code or s.act.act_name} § {s.section_number}"
            if label not in tags:
                tags.append(label)
        return tags[:4]


class LegalScenarioDetailSerializer(serializers.ModelSerializer):
    category = LawCategorySerializer(read_only=True)
    sections = LawSectionSerializer(many=True, read_only=True)

    class Meta:
        model = LegalScenario
        fields = [
            'id',
            'title',
            'slug',
            'category',
            'situation_summary',
            'what_to_do',
            'official_portal_url',
            'helpline_number',
            'is_featured',
            'display_order',
            'sections',
            'created_at',
            'updated_at',
        ]
