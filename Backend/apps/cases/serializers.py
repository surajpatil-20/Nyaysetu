from rest_framework import serializers
from .models import Case, Party, CaseParty, CaseJudge, CaseEvent, CaseCitation
from apps.courts.serializers import CourtSerializer, JudgeSerializer


class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = ['id', 'name', 'party_type', 'created_at']


class CasePartySerializer(serializers.ModelSerializer):
    party_name = serializers.CharField(source='party.name', read_only=True)
    party_type = serializers.CharField(source='party.party_type', read_only=True)

    class Meta:
        model = CaseParty
        fields = ['id', 'case', 'party', 'party_name', 'party_type', 'role', 'party_order']


class CaseJudgeSerializer(serializers.ModelSerializer):
    judge_name = serializers.CharField(source='judge.name', read_only=True)
    judge_designation = serializers.CharField(source='judge.designation', read_only=True)

    class Meta:
        model = CaseJudge
        fields = ['id', 'case', 'judge', 'judge_name', 'judge_designation', 'role', 'bench_order']


class CaseEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseEvent
        fields = ['id', 'case', 'event_date', 'event_type', 'title', 'description', 'document', 'source_url', 'created_at']


class CaseCitationSerializer(serializers.ModelSerializer):
    source_case_number = serializers.CharField(source='source_case.case_number', read_only=True)
    cited_case_number = serializers.CharField(source='cited_case.case_number', read_only=True, default=None)

    class Meta:
        model = CaseCitation
        fields = [
            'id', 'source_case', 'source_case_number',
            'cited_case', 'cited_case_number',
            'citation_text', 'source_document', 'page_number', 'created_at'
        ]


class CaseListSerializer(serializers.ModelSerializer):
    court_name = serializers.CharField(source='court.court_name', read_only=True)
    court_type = serializers.CharField(source='court.court_type', read_only=True)

    class Meta:
        model = Case
        fields = [
            'id', 'case_number', 'cnr_number', 'case_title',
            'case_type', 'court', 'court_name', 'court_type',
            'filing_date', 'decision_date', 'status',
            'source_name', 'source_url', 'created_at'
        ]


class CaseDetailSerializer(serializers.ModelSerializer):
    court = CourtSerializer(read_only=True)
    case_parties = CasePartySerializer(many=True, read_only=True)
    case_judges = CaseJudgeSerializer(many=True, read_only=True)
    timeline_events = CaseEventSerializer(many=True, read_only=True)
    citations_made = CaseCitationSerializer(many=True, read_only=True)
    citations_received = CaseCitationSerializer(many=True, read_only=True)

    class Meta:
        model = Case
        fields = '__all__'

