from django.core.management.base import BaseCommand
from cms.models import BoardRole


ROLES = [
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


class Command(BaseCommand):
    help = "Seed des postes du bureau exécutif"

    def handle(self, *args, **kwargs):

        created_count = 0

        for index, titre in enumerate(ROLES, start=1):

            obj, created = BoardRole.objects.get_or_create(
                titre=titre,
                defaults={
                    "ordre": index,
                    "actif": True,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f" Créé : {titre}"))
            else:
                self.stdout.write(f" Existe déjà : {titre}")

        self.stdout.write(self.style.SUCCESS(
            f"\n Seed terminé : {created_count} nouveaux rôles ajoutés."
        ))