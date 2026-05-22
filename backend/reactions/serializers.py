from rest_framework import serializers
from .models import Reaction


class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = ['id', 'reaction_type', 'created_at']
        read_only_fields = ['created_at']


class ReactionSummarySerializer(serializers.Serializer):
    reaction_type = serializers.CharField()
    count = serializers.IntegerField()
    reacted = serializers.BooleanField()
