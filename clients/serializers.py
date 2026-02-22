from rest_framework import serializers
from .models import ClientProfile
from django.contrib.auth import get_user_model
import secrets
from django.core.mail import send_mail

User = get_user_model()


class ClientRegistrationSerializer(serializers.ModelSerializer):

    PROVIDERS_PUBLICS = [
        "gmail.com",
        "yahoo.com",
        "hotmail.com",
        "outlook.com",
    ]

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
        domain = email.split("@")[1]

        auto_valide = domain not in self.PROVIDERS_PUBLICS

        password = secrets.token_urlsafe(10)

        # -----------------------------
        # Création USER
        # -----------------------------
        user = User.objects.create_user(
            email=email,
            password=password,
            role="CLIENT",
            is_active=auto_valide,
        )

        # -----------------------------
        # Création PROFILE
        # -----------------------------
        client = ClientProfile.objects.create(
            user=user,
            est_verifie=auto_valide,
            **validated_data
        )

        # -----------------------------
        # EMAIL SELON CAS
        # -----------------------------
        if auto_valide:

            send_mail(
                subject="Activation de votre espace client AMEE",
                message=(
                    f"Bonjour {client.nom_contact},\n\n"
                    f"Votre espace client AMEE est maintenant actif.\n\n"
                    f"Identifiant : {email}\n"
                    f"Mot de passe temporaire : {password}\n\n"
                    f"Nous vous recommandons de modifier votre mot de passe après connexion.\n\n"
                    f"Connexion : https://amee.org/login/\n\n"
                    f"L’équipe AMEE"
                ),
                from_email=None,
                recipient_list=[email],
                fail_silently=True,
            )

        else:

            send_mail(
                subject="Demande d'accès AMEE en cours de vérification",
                message=(
                    f"Bonjour {client.nom_contact},\n\n"
                    f"Votre demande d'accès à la plateforme AMEE a bien été reçue.\n\n"
                    f"Notre équipe va vérifier vos informations "
                    f"avant activation de votre espace client.\n\n"
                    f"Vous recevrez un email dès validation.\n\n"
                    f"L’équipe AMEE"
                ),
                from_email=None,
                recipient_list=[email],
                fail_silently=True,
            )

        return client