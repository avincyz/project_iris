from rest_framework import serializers
from .models import GameSession

class GameSessionStartSerializer(serializers.Serializer):

    incident_type = serializers.ChoiceField(choices = GameSession.INCIDENT_TYPE_CHOICES)

    difficulty = serializers.IntegerField(min_value = 1, max_value = 3)

class GenerateQuestionsSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()

class AnswerQuestionSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
    stage_name = serializers.CharField()
    selected_option_id = serializers.CharField()