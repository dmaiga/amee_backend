from django.core.management.base import BaseCommand
from cms.models import Mandat
from datetime import date


class Command(BaseCommand):
    help = "Seed du mandat actif 2025-2026"

    def handle(self, *args, **kwargs):

        mandat, created = Mandat.objects.get_or_create(
            nom="Mandat 2025-2026",
            defaults={
                "date_debut": date(2025, 1, 1),
                "date_fin": date(2026, 12, 31),
                "actif": True,
                "mot_president": "Message officiel du président pour ce mandat",
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(" Mandat créé"))
        else:
            self.stdout.write(" Mandat déjà existant")

        # Sécurité : garantir qu'il est actif
        mandat.actif = True
        mandat.save()

        self.stdout.write(self.style.SUCCESS(" Seed mandat terminé"))