from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from cms.models import Article, Resource, Opportunity

User = get_user_model()

class Command(BaseCommand):
    help = "Seed CMS demo content with bilingual support for Articles"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Seeding CMS demo content..."))

        author = User.objects.filter(is_superuser=True).first()
        if not author:
            self.stdout.write(self.style.ERROR("Aucun superuser trouvé. Créez-en un avec createsuperuser."))
            return

        now = timezone.now()

        # ==========================================
        # ARTICLES (Bilingues)
        # ==========================================
        articles_data = [
            {
                "titre_fr": "Lancement officiel du nouveau mandat 2025-2027",
                "titre_en": "Official launch of the 2025-2027 mandate",
                "type": "COMMUNIQUE",
                "contenu_fr": "Le bureau exécutif annonce le lancement officiel du nouveau mandat.",
                "contenu_en": "The executive board announces the official launch of the new mandate.",
            },
            {
                "titre_fr": "Atelier de renforcement des capacités",
                "titre_en": "Capacity building workshop",
                "type": "FORMATION",
                "contenu_fr": "Un atelier sera organisé pour renforcer les compétences.",
                "contenu_en": "A workshop will be organized to strengthen skills.",
            },
        ]

        for data in articles_data:
            # On utilise get_or_create sur le titre_fr pour éviter les doublons
            article, created = Article.objects.get_or_create(
                titre_fr=data["titre_fr"],
                defaults={
                    "titre_en": data["titre_en"],
                    "type": data["type"],
                    "contenu_fr": data["contenu_fr"],
                    "contenu_en": data["contenu_en"],
                    "publie": True,
                    "date_publication": now - timedelta(days=1),
                    "publie_par": author,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Article bilingue créé : {article.titre_fr}"))

        # ==========================================
        # RESSOURCES (Français uniquement - MVT)
        # ==========================================
        resources_data = [
            {
                "titre": "Guide méthodologique d’évaluation environnementale",
                "categorie": "GUIDE",
                "description": "Guide technique officiel pour les praticiens au Mali.",
            },
            {
                "titre": "Rapport annuel d'activités AMEE 2024",
                "categorie": "RAPPORT",
                "description": "Bilan des activités réalisées l'année précédente.",
            },
        ]

        for data in resources_data:
            # On vérifie si les champs categorie existent bien dans ton modèle
            resource, created = Resource.objects.get_or_create(
                titre=data["titre"],
                defaults={
                    "description": data["description"],
                    # "categorie": data["categorie"], # Assure-toi que ce champ existe
                    "publie_par": author,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Ressource créée : {resource.titre}"))

        # ==========================================
        # OPPORTUNITÉS (Français uniquement - MVT)
        # ==========================================
        opportunities_data = [
            {
                "titre": "Consultant senior en évaluation environnementale",
                "type": "EMPLOI",
                "description": "Recrutement d’un consultant pour mission à Bamako.",
                "date_limite": now.date() + timedelta(days=20),
            },
        ]

        for data in opportunities_data:
            opp, created = Opportunity.objects.get_or_create(
                titre=data["titre"],
                defaults={
                    "description": data["description"],
                    "type": data["type"],
                    "date_limite": data["date_limite"],
                    "publie": True,
                    "publie_par": author,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Opportunité créée : {opp.titre}"))

        self.stdout.write(self.style.SUCCESS("--- Seed CMS terminé ---"))