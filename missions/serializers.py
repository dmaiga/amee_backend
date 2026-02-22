from rest_framework import serializers
from missions.models import Mission


class MissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Mission
        fields = "__all__"
        read_only_fields = ("client", "statut", "cree_le")