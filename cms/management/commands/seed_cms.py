from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

from cms.models import Article, Resource, Opportunity

User = get_user_model()


class Command(BaseCommand):
    help = "Seed CMS demo content"

    def handle(self, *args, **kwargs):

        self.stdout.write(self.style.WARNING("Seeding CMS demo content..."))

        author = User.objects.filter(is_superuser=True).first()

        if not author:
            self.stdout.write(self.style.ERROR("Aucun superuser trouvé."))
            return

        now = timezone.now()

        # ===============================
        # ARTICLES
        # ===============================

        articles_data = [
            {
                "titre": "Lancement officiel du nouveau mandat 2025-2027",
                "type": "COMMUNIQUE",
                "contenu": "Le bureau exécutif annonce le lancement officiel du nouveau mandat avec des objectifs stratégiques ambitieux.",
            },
            {
                "titre": "Atelier de renforcement des capacités en évaluation environnementale",
                "type": "FORMATION",
                "contenu": "Un atelier sera organisé pour renforcer les compétences techniques des membres.",
            },
            {
                "titre": "Appel à participation – Conférence régionale",
                "type": "APPEL",
                "contenu": "Les membres sont invités à participer à la conférence régionale sur la gouvernance environnementale.",
            },
            {
                "titre": "Partenariat stratégique avec une institution internationale",
                "type": "PARTENARIAT",
                "contenu": "Signature d’un protocole d’accord pour renforcer la coopération institutionnelle.",
            },
        ]

        for data in articles_data:
            article, created = Article.objects.get_or_create(
                titre=data["titre"],
                defaults={
                    "type": data["type"],
                    "contenu": data["contenu"],
                    "publie": True,
                    "date_publication": now - timedelta(days=2),
                    "publie_par": author,
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Article créé : {article.titre}"))

        # ===============================
        # RESSOURCES
        # ===============================

        resources_data = [
            {
                "titre": "Guide méthodologique d’évaluation environnementale",
                "categorie": "GUIDE",
                "description": "Guide technique officiel pour les praticiens.",
            },
            {
                "titre": "Rapport annuel 2024",
                "categorie": "RAPPORT",
                "description": "Rapport consolidé des activités et performances.",
            },
        ]

        for data in resources_data:
            resource, created = Resource.objects.get_or_create(
                titre=data["titre"],
                defaults={
                    "description": data["description"],
                    "categorie": data["categorie"],
                    "reserve_aux_membres": True,
                    "publie_par": author,
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Ressource créée : {resource.titre}"))

        # ===============================
        # OPPORTUNITÉS
        # ===============================

        opportunities_data = [
            {
                "titre": "Consultant senior en évaluation environnementale",
                "type": "EMPLOI",
                "description": "Recrutement d’un consultant senior pour mission nationale.",
                "date_limite": timezone.now().date() + timedelta(days=30),
            },
            {
                "titre": "Appel d’offre – Étude d’impact social",
                "type": "APPEL_OFFRE",
                "description": "Appel d’offre pour une étude d’impact social à Bamako.",
                "date_limite": timezone.now().date() + timedelta(days=15),
            },
        ]

        for data in opportunities_data:
            opportunity, created = Opportunity.objects.get_or_create(
                titre=data["titre"],
                defaults={
                    "description": data["description"],
                    "type": data["type"],
                    "date_limite": data["date_limite"],
                    "reserve_aux_membres": True,
                    "publie": True,
                    "publie_par": author,
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Opportunité créée : {opportunity.titre}"))

        self.stdout.write(self.style.SUCCESS("CMS seed terminé avec succès."))