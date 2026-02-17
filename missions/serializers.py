from rest_framework import serializers
from missions.models import Mission


class MissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Mission
        fields = [
            'id',
            'titre',
            'description',
            'domaine',
            'localisation',
            'duree_estimee_jours',
            'statut',
            'cree_le',
        ]
        read_only_fields = ['statut', 'cree_le']
