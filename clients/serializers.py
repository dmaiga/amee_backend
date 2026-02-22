from rest_framework import serializers
from .models import ClientProfile
from django.contrib.auth import get_user_model
import secrets
from django.core.mail import send_mail

User = get_user_model()


class ClientRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClientProfile
        fields = [
            "nom_entreprise",
            "secteur_activite",
            "email_pro",
            "telephone_pro",
            "nom_contact",
            "fonction_contact",
        ]

    def create(self, validated_data):

        email = validated_data["email_pro"].lower().strip()

        # 🔐 génération password
        password = secrets.token_urlsafe(8)

        # création user
        user = User.objects.create_user(
            email=email,
            password=password,
            role="CLIENT",
        )

        client = ClientProfile.objects.create(
            user=user,
            **validated_data
        )

        # 📧 envoi accès
        send_mail(
            subject="Accès plateforme AMEE",
            message=(
                f"Bonjour,\n\n"
                f"Votre accès a été créé.\n\n"
                f"Login : {email}\n"
                f"Mot de passe : {password}\n\n"
                f"Connectez-vous ici : https://amee.org/login/"
            ),
            from_email=None,
            recipient_list=[email],
            fail_silently=True,
        )

        return client