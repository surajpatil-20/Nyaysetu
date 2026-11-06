from rest_framework import serializers
from .models import Court, Judge, JudgeCourtHistory


class JudgeCourtHistorySerializer(serializers.ModelSerializer):
    court_name = serializers.CharField(source='court.court_name', read_only=True)

    class Meta:
        model = JudgeCourtHistory
        fields = ['id', 'court', 'court_name', 'designation', 'start_date', 'end_date']


class JudgeSerializer(serializers.ModelSerializer):
    current_court_name = serializers.CharField(source='current_court.court_name', read_only=True)
    court_history = JudgeCourtHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Judge
        fields = ['id', 'name', 'current_court', 'current_court_name', 'designation', 'source_url', 'court_history', 'created_at']


class CourtSerializer(serializers.ModelSerializer):
    sitting_judges_count = serializers.IntegerField(source='sitting_judges.count', read_only=True)

    class Meta:
        model = Court
        fields = '__all__'

