from rest_framework import serializers
from .config.choices import (INCIDENT_TYPE_CHOICES,
                             DIFFICULTY_CHOICES)

class GameSessionStartSerializer(serializers.Serializer):
    incident_type = serializers.ChoiceField(choices = INCIDENT_TYPE_CHOICES)
    difficulty = serializers.ChoiceField(choices = DIFFICULTY_CHOICES)

class GenerateQuestionsSerializer(serializers.Serializer):
    questions_per_stage = serializers.IntegerField(default = 2)

class AnswerQuestionSerializer(serializers.Serializer):
    question_uid = serializers.CharField()
    selected_option_id = serializers.CharField()