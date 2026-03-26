from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from cms.models import BoardMembership, BoardRole, Mandat

User = get_user_model()


MAPPING = [
    ("sm.diakite@amee.com", "Président"),
    ("f.traore@amee.com", "Secrétaire général"),
    ("m.gaba@amee.com", "Secrétaire général adjoint"),
    ("n.kone@amee.com", "Secrétaire à l’Organisation et à la Mobilisation"),
    ("s.yalcouye@amee.com", "Premier Secrétaire à l’Organisation et à la Mobilisation"),
    ("m.kone@amee.com", "Deuxième Secrétaire à l’Organisation et à la Mobilisation"),
    ("a.dicko@amee.com", "Secrétaire à la Formation et au Partenariat"),
    ("s.diakite@amee.com", "Premier Secrétaire à la Formation et au Partenariat"),
    ("s.dembele@amee.com", "Secrétaire adjoint à la Formation et au Partenariat"),
    ("i.camara@amee.com", "Secrétaire à l’Information et à la Communication"),
    ("a.camara@amee.com", "Secrétaire Adjoint à l’Information et à la Communication"),
    ("i.sidibe@amee.com", "Secrétaire aux métiers de l’environnement"),
    ("c.sangare@amee.com", "Premier Secrétaire aux métiers de l’environnement"),
    ("h.maiga@amee.com", "Deuxième Secrétaire aux métiers de l’environnement"),
    ("e.saye@amee.com", "Secrétaire aux conflits"),
    ("l.traore@amee.com", "Trésorier"),
    ("h.sidibe@amee.com", "Trésorier Adjoint"),
    ("m.dembele@amee.com", "1er Commissaire aux comptes"),
    ("a.plea@amee.com", "2ème Commissaire aux comptes"),
]


class Command(BaseCommand):
    help = "Seed Board Membership"

    def handle(self, *args, **kwargs):

        mandat = Mandat.objects.filter(actif=True).first()

        if not mandat:
            self.stdout.write(self.style.ERROR(" Aucun mandat actif"))
            return

        for email, role_name in MAPPING:

            try:
                user = User.objects.get(email=email)
                role = BoardRole.objects.get(titre=role_name)

                membership = user.membership  # important

                obj, created = BoardMembership.objects.get_or_create(
                    membership=membership,
                    mandat=mandat,
                    role=role
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"{email} -> {role_name}"))
                else:
                    self.stdout.write(f" Existe déjà : {email}")

            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f" User introuvable: {email}"))

            except BoardRole.DoesNotExist:
                self.stdout.write(self.style.ERROR(f" Role introuvable: {role_name}"))

        self.stdout.write(self.style.SUCCESS("Seed BoardMembership terminé"))