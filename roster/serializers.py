from rest_framework import serializers
from roster.models import ConsultantProfile


class ConsultantSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(source='user.email', read_only=True)
    id_membre = serializers.CharField(
        source='user.id_membre_association',
        read_only=True
    )

    class Meta:
        model = ConsultantProfile
        fields = [
            'email',
            'id_membre',
            'statut',
            'domaine_expertise',
            'annees_experience',
            'resume_profil'
        ]

class ConsultantPublicSerializer(serializers.ModelSerializer):

    nom_complet = serializers.SerializerMethodField()
    id_membre = serializers.CharField(
        source='user.id_membre_association',
        read_only=True
    )

    recommande_amee = serializers.SerializerMethodField()

    class Meta:
        model = ConsultantProfile
        fields = [
            'nom_complet',
            'id_membre',
            'domaine_expertise',
            'annees_experience',
            'resume_profil',
            'recommande_amee',
        ]

    def get_nom_complet(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    def get_recommande_amee(self, obj):
        return obj.user.est_recommande_amee
