from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from roster.models import ConsultantProfile


class ConsultantSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(source="user.email", read_only=True)
    id_membre = serializers.CharField(
        source="user.id_membre_association",
        read_only=True
    )

    class Meta:
        model = ConsultantProfile
        fields = [
            "email",
            "id_membre",
            "statut",
            "domaine_expertise",
            "annees_experience",
            
        ]


class ConsultantPublicSerializer(serializers.ModelSerializer):

    nom_complet = serializers.SerializerMethodField()
    recommande_amee = serializers.SerializerMethodField()

    resume_public = serializers.CharField(
        source="public_profile.resume_public"
    )

    langues = serializers.CharField(
        source="public_profile.langues"
    )

    secteurs_experience = serializers.CharField(
        source="public_profile.secteurs_experience"
    )

    experience_geographique = serializers.CharField(
        source="public_profile.experience_geographique"
    )

    statut_disponibilite = serializers.CharField(
        source="public_profile.statut_disponibilite"
    )

    class Meta:
        model = ConsultantProfile
        fields = [
            "nom_complet",
            "domaine_expertise",
            "annees_experience",
            "resume_public",
            "langues",
            "secteurs_experience",
            "experience_geographique",
            "statut_disponibilite",
            "recommande_amee",
        ]

    def get_nom_complet(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    def get_recommande_amee(self, obj):
        return obj.user.est_recommande_amee

class MessageResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()


class MonProfilRosterResponseSerializer(serializers.Serializer):
    a_un_profil = serializers.BooleanField()
    statut = serializers.CharField(required=False)
    est_consultant = serializers.BooleanField(required=False)
    profil = ConsultantSerializer(required=False)