from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

from missions.models import Mission
from portals.models import ClientProfile

User = get_user_model()


class Command(BaseCommand):
    help = "Seed missions for validated clients only"

    def handle(self, *args, **kwargs):

        self.stdout.write(self.style.WARNING("Seeding missions..."))

        # Clients validés uniquement
        validated_clients = ClientProfile.objects.filter(
            est_verifie=True,
            user__is_active=True
        )

        if not validated_clients.exists():
            self.stdout.write(self.style.ERROR("Aucun client validé trouvé."))
            return

        missions_data = [
            {
                "titre": "Évaluation environnementale d’un projet minier",
                "domaine": "Environnement",
                "budget": 15000000,
                "duree": 30,
            },
            {
                "titre": "Audit social et impact communautaire",
                "domaine": "Social",
                "budget": 8000000,
                "duree": 20,
            },
            {
                "titre": "Étude d’impact environnemental - Infrastructures routières",
                "domaine": "Infrastructure",
                "budget": 25000000,
                "duree": 45,
            },
            {
                "titre": "Analyse stratégique climat et résilience",
                "domaine": "Climat",
                "budget": 12000000,
                "duree": 25,
            },
        ]

        now = timezone.now()

        for client_profile in validated_clients:

            for data in missions_data:

                mission = Mission.objects.create(
                    type_publication="PUBLIQUE",
                    client=client_profile.user,
                    titre=data["titre"],
                    description="Mission professionnelle nécessitant expertise technique et analyse approfondie.",
                    objectifs="Réaliser une évaluation complète et produire un rapport détaillé.",
                    livrables_attendus="Rapport final, recommandations stratégiques.",
                    domaine=data["domaine"],
                    localisation="Mali",
                    duree_estimee_jours=data["duree"],
                    budget_estime=data["budget"],
                    statut="ACTIVE",
                    date_fin=now.date() + timedelta(days=30),
                    publie_le=now,
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Mission créée : {mission.titre} -> {client_profile.nom_entreprise}"
                    )
                )

        self.stdout.write(self.style.SUCCESS("Seed missions terminé."))