from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from portals.models import ClientProfile
import secrets

User = get_user_model()


class Command(BaseCommand):
    help = "Seed test clients (auto-validés + en attente)"

    def handle(self, *args, **kwargs):

        providers_publics = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]

        clients_data = [
            # AUTO VALIDES
            {
                "email": "contact@ecobank.com",
                "nom_entreprise": "Ecobank Mali",
                "secteur": "Banque",
                "contact": "Moussa Traore"
            },
            {
                "email": "info@orange.ml",
                "nom_entreprise": "Orange Mali",
                "secteur": "Télécommunication",
                "contact": "Fatoumata Diallo"
            },
            {
                "email": "admin@africaconsulting.ml",
                "nom_entreprise": "Africa Consulting",
                "secteur": "Consulting",
                "contact": "Oumar Keita"
            },
            {
                "email": "contact@mines.gov.ml",
                "nom_entreprise": "Ministère des Mines",
                "secteur": "Institution publique",
                "contact": "Ibrahim Maiga"
            },
            {
                "email": "rh@sonatel.ml",
                "nom_entreprise": "Sonatel Mali",
                "secteur": "Télécom",
                "contact": "Awa Konate"
            },

            # EN ATTENTE
            {
                "email": "entreprise123@gmail.com",
                "nom_entreprise": "Startup Vision",
                "secteur": "Startup",
                "contact": "Amadou Coulibaly"
            },
            {
                "email": "business@yahoo.com",
                "nom_entreprise": "Global Trade",
                "secteur": "Commerce",
                "contact": "Salimata Cisse"
            },
            {
                "email": "recrutement@outlook.com",
                "nom_entreprise": "Talent Recruit",
                "secteur": "RH",
                "contact": "Boubacar Diarra"
            },
        ]

        for data in clients_data:

            email = data["email"].lower()

            if User.objects.filter(email=email).exists():
                self.stdout.write(f"{email} déjà existant.")
                continue

            domain = email.split("@")[1]
            auto_valide = domain not in providers_publics

            password = 'changeMe'

            user = User.objects.create_user(
                email=email,
                password=password,
                role="CLIENT",
                is_active=auto_valide,
            )

            ClientProfile.objects.create(
                user=user,
                email_pro=email,
                nom_entreprise=data["nom_entreprise"],
                secteur_activite=data["secteur"],
                nom_contact=data["contact"],
                telephone_pro="00000000",
                est_verifie=auto_valide,
                statut_onboarding="VALIDE" if auto_valide else "EN_ATTENTE",
            )

            status = "AUTO-VALIDÉ" if auto_valide else "EN ATTENTE"

            self.stdout.write(
                self.style.SUCCESS(f"{data['nom_entreprise']} -> {status}")
            )

        self.stdout.write(self.style.SUCCESS("Seed terminé avec succès."))