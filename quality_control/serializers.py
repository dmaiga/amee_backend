from rest_framework import serializers
from quality_control.models import Feedback
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault


class FeedbackSerializer(serializers.ModelSerializer):

    client = serializers.HiddenField(
        default=CurrentUserDefault()
    )

    contact_request = serializers.HiddenField(default=None)

    class Meta:
        model = Feedback
        fields = [
            "id",
            "client",
            "contact_request",
            "note",
            "commentaire",
            "incident_signale",
            "description_incident",
            "cree_le",
        ]
        read_only_fields = ("cree_le",)
