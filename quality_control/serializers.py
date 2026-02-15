from rest_framework import serializers
from .models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):

    class Meta:
        model = Feedback
        fields = [
            "id",
            "contact_request",
            "note",
            "commentaire",
            "cree_le",
        ]
        read_only_fields = ("cree_le",)
