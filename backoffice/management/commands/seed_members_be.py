from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tresorerie.services import TresorerieService
from memberships.models import Membership
from roster.models import ConsultantProfile
from django.utils import timezone

User = get_user_model()


MEMBRES = [
    ("Samballa Mady DIAKITE", "sm.diakite@amee.com"),
    ("Fousseyni T. TRAORE", "f.traore@amee.com"),
    ("Mamadou GABA", "m.gaba@amee.com"),
    ("N'Faly KONE", "n.kone@amee.com"),
    ("Soumaïla Seydou YALCOUYE", "s.yalcouye@amee.com"),
    ("Mme Mafing KONE", "m.kone@amee.com"),
    ("Ahmadou H. DICKO", "a.dicko@amee.com"),
    ("Sidiki DIAKITE", "s.diakite@amee.com"),
    ("Saran Niakoro DEMBELE", "s.dembele@amee.com"),
    ("Ibrahima CAMARA", "i.camara@amee.com"),
    ("Mme Assa CAMARA", "a.camara@amee.com"),
    ("Issa M. SIDIBE", "i.sidibe@amee.com"),
    ("Coumba dite Astan SANGARE", "c.sangare@amee.com"),
    ("Habiboulaye D. MAIGA", "h.maiga@amee.com"),
    ("Elisée SAYE", "e.saye@amee.com"),
    ("Lassana TRAORE", "l.traore@amee.com"),
    ("Hawa SIDIBE", "h.sidibe@amee.com"),
    ("Modibo DEMBELE", "m.dembele@amee.com"),
    ("Mme Assitan PLEA", "a.plea@amee.com"),
]


class Command(BaseCommand):
    help = "Seed membres BE + validation consultant"

    def handle(self, *args, **kwargs):

        admin = User.objects.filter(is_superuser=True).first()

        for nom_complet, email in MEMBRES:

            # -------------------------
            # SPLIT NOM
            # -------------------------
            parts = nom_complet.replace("Mme ", "").split(" ")
            first_name = parts[0]
            last_name = " ".join(parts[1:])

            # -------------------------
            # ADHESION
            # -------------------------
            TresorerieService.enregistrer_paiement(
                user=admin,
                data={
                    "type_transaction": "ENTREE",
                    "categorie": "ADHESION",
                    "montant": 5000,
                    "email_payeur": email,
                    "description": "Seed BE",
                }
            )

            user = User.objects.get(email=email)

            user.first_name = first_name
            user.last_name = last_name
            user.save()

            # -------------------------
            # COTISATION
            # -------------------------
            TresorerieService.enregistrer_paiement(
                user=admin,
                data={
                    "type_transaction": "ENTREE",
                    "categorie": "COTISATION",
                    "montant": 10000,
                    "membre": user,
                    "description": "Cotisation BE",
                }
            )

            # -------------------------
            # OVERRIDE MEMBERSHIP
            # -------------------------
            membership = Membership.objects.get(user=user)

            membership.statut = "VALIDE"
            membership.date_activation = timezone.now().date()
            membership.date_expiration = timezone.now().date().replace(year=timezone.now().year + 1)
            membership.save()

            # -------------------------
            # CONSULTANT PROFILE
            # -------------------------
            profil, _ = ConsultantProfile.objects.get_or_create(
                user=user,
                defaults={
                    "statut": "VALIDE",
                    "eligibilite_validee": True,
                    "date_validation": timezone.now(),
                    "est_disponible": True,
                }
            )

            # -------------------------
            # FORCE VALIDATION
            # -------------------------
            profil.statut = "VALIDE"
            profil.eligibilite_validee = True
            profil.date_validation = timezone.now()
            profil.save()

            # -------------------------
            # ROLE FINAL
            # -------------------------
            user.role = "CONSULTANT"
            user.save()

            self.stdout.write(self.style.SUCCESS(f" {nom_complet} OK"))

        self.stdout.write(self.style.SUCCESS(" Seed complet BE + consultants"))