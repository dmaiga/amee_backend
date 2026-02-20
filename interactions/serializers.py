from rest_framework import serializers
from interactions.models import ContactRequest
from missions.serializers import MissionSerializer
from django.contrib.auth import get_user_model
from roster.models import ConsultantProfile

User = get_user_model()



class ContactRequestSerializer(serializers.ModelSerializer):

    consultant = serializers.PrimaryKeyRelatedField(
        queryset=ConsultantProfile.objects.filter(statut="VALIDE"),
        write_only=True
    )

    class Meta:
        model = ContactRequest
        fields = [
            "id",
            "mission",
            "consultant",
            "message",
            "duree_estimee_jours",
            "statut",
            "cree_le",
        ]
        read_only_fields = ["statut", "cree_le"]

    def create(self, validated_data):
        profil = validated_data.pop("consultant")
        validated_data["consultant"] = profil.user
        return super().create(validated_data)

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
