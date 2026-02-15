from rest_framework import serializers
from interactions.models import ContactRequest


class ContactRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactRequest
        fields = [
            'id',
            'mission',
            'consultant',
            'message',
            'duree_estimee_jours',
            'statut',
            'cree_le'
        ]
        read_only_fields = ['statut', 'cree_le']

from missions.serializers import MissionSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class ContactRequestReadSerializer(serializers.ModelSerializer):

    mission = MissionSerializer(read_only=True)
    consultant_nom = serializers.CharField(
        source='consultant.get_full_name',
        read_only=True
    )
    client_nom = serializers.CharField(
        source='client.get_full_name',
        read_only=True
    )

    class Meta:
        model = ContactRequest
        fields = [
            'id',
            'mission',
            'consultant_nom',
            'client_nom',
            'statut',
            'est_collaboration_validee',
            'cree_le',
        ]

class UpdateContactStatusSerializer(serializers.Serializer):
    statut = serializers.ChoiceField(
        choices=[
            'MISSION_CONFIRME',
            'REFUSE',
            'SANS_SUITE'
        ]
    )

class TerminerMissionSerializer(serializers.Serializer):
    confirmer = serializers.BooleanField()
