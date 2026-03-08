# memberships/serializers.py

from rest_framework import serializers
from memberships.models import Membership


from rest_framework import serializers
from django.contrib.auth import get_user_model
from memberships.models import Membership

User = get_user_model()

from rest_framework import serializers
from django.contrib.auth import get_user_model
from memberships.models import Membership

User = get_user_model()

class MembershipRegistrationSerializer(serializers.Serializer):

    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone = serializers.CharField(required=False)

    eligibilite_option = serializers.ChoiceField(
        choices=Membership.ELIGIBILITE
    )

    diplome_niveau = serializers.ChoiceField(
        choices=Membership.DIPLOME_NIVEAU,
        required=False
    )

    diplome_intitule = serializers.CharField(required=False)
    annee_diplome = serializers.CharField(required=False)

    cv_document = serializers.FileField(required=False)
    diplome_document = serializers.FileField(required=False)

    def create(self, validated_data):

        email = validated_data["email"]

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": validated_data["first_name"],
                "last_name": validated_data["last_name"],
                "phone": validated_data.get("phone"),
                "role": "VISITEUR",  
                "is_active": True,
            }
        )

        # Si user existait déjà → on met à jour infos de base
        if not created:
            user.first_name = validated_data["first_name"]
            user.last_name = validated_data["last_name"]
            user.phone = validated_data.get("phone")
            user.save(update_fields=["first_name", "last_name", "phone"])

        Membership.objects.update_or_create(
            user=user,
            defaults={
                "eligibilite_option":
                    validated_data["eligibilite_option"],
                "diplome_niveau":
                    validated_data.get("diplome_niveau"),
                "diplome_intitule":
                    validated_data.get("diplome_intitule"),
                "annee_diplome":
                    validated_data.get("annee_diplome"),                  
                "cv_document":
                    validated_data.get("cv_document"),
                "diplome_document":
                    validated_data.get("diplome_document"),
                "statut": "EN_ATTENTE",
            }
        )

        return user