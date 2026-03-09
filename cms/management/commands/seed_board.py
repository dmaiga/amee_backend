from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date

from cms.models import Mandat, BoardRole


class Command(BaseCommand):
    help = "Seed initial Mandat and Board Roles"

    def handle(self, *args, **kwargs):

        self.stdout.write(self.style.WARNING("Seeding board data..."))

        # Supprimer anciens rôles (optionnel si environnement dev)


        # Désactiver anciens mandats
        Mandat.objects.filter(actif=True).update(actif=False)

        # Création mandat actif
        mandat, created = Mandat.objects.get_or_create(
            nom="Mandat 2025-2027",
            defaults={
                "date_debut": date(2025, 1, 1),
                "date_fin": date(2027, 12, 31),
                "actif": True,
                "mot_president": "Message officiel du président pour le mandat 2025-2027."
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS("Mandat créé."))
        else:
            self.stdout.write("Mandat déjà existant.")

        roles = [
            "Président",
            "Secrétaire général",
            "Secrétaire général adjoint",
            "Secrétaire à l’Organisation et à la Mobilisation",
            "Premier Secrétaire à l’Organisation et à la Mobilisation",
            "Deuxième Secrétaire à l’Organisation et à la Mobilisation",
            "Secrétaire à la Formation et au Partenariat",
            "Premier Secrétaire à la Formation et au Partenariat",
            "Secrétaire adjoint à la Formation et au Partenariat",
            "Secrétaire à l’Information et à la Communication",
            "Secrétaire Adjoint à l’Information et à la Communication",
            "Secrétaire aux métiers de l’environnement",
            "Premier Secrétaire aux métiers de l’environnement",
            "Deuxième Secrétaire aux métiers de l’environnement",
            "Secrétaire aux conflits",
            "Trésorier",
            "Trésorier Adjoint",
            "1er Commissaire aux comptes",
            "2ème Commissaire aux comptes",
        ]

        for index, titre in enumerate(roles, start=1):
            BoardRole.objects.create(
                titre=titre,
                ordre=index,
                actif=True
            )

        self.stdout.write(self.style.SUCCESS("Board roles seeded successfully."))