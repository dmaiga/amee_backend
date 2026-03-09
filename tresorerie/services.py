from memberships.models import Membership
from tresorerie.models import Transaction
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.db import transaction as db_transaction
from django.core.mail import send_mail
from django.conf import settings
import secrets

User = get_user_model()


# =====================================================
# EMAIL
# =====================================================
def envoyer_email_enrolement(user, password_temporaire):

    sujet = "Bienvenue — Activation de votre compte membre"

    message = f"""
Bonjour {user.first_name or ''},

Votre adhésion a été enregistrée.

Email : {user.email}
Mot de passe temporaire : {password_temporaire}

Veuillez modifier votre mot de passe après connexion.
L'equipe AMEE

"""

    send_mail(
        sujet,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


# =====================================================
# MEMBER ID
# =====================================================
def generate_member_id():
    year = timezone.now().year

    last = User.objects.filter(
        id_membre_association__startswith=f"MEM-{year}-"
    ).order_by("-id_membre_association").first()

    if not last or not last.id_membre_association:
        num = 1
    else:
        num = int(last.id_membre_association.split("-")[-1]) + 1

    return f"MEM-{year}-{num:03d}"


# =====================================================
# REGLES METIER DECLENCHEES PAR TRANSACTION
# =====================================================
def appliquer_transaction(transaction):

    if transaction.type_transaction != "ENTREE":
        return

    user = transaction.membre

    # création auto membre via email payeur
    if not user and transaction.email_payeur:
        user, _ = User.objects.get_or_create(
            email=transaction.email_payeur,
            defaults={"role": "MEMBER"}
        )
        transaction.membre = user
        transaction.save(update_fields=["membre"])

    # =========================
    # ADHESION MEMBRE
    # =========================
    if transaction.categorie == "ADHESION" and user:

        membership, _ = Membership.objects.get_or_create(user=user)

        is_new = False
        temp_password = None

        if not user.id_membre_association:
            user.id_membre_association = generate_member_id()
            is_new = True

        if is_new:
            password = secrets.token_urlsafe(10)
            temp_password = password
            user.set_password(temp_password)

        user.role = "MEMBER"
        user.save()

        if is_new:
            envoyer_email_enrolement(user, temp_password)

        return

    # =========================
    # COTISATION MEMBRE
    # =========================
    if transaction.categorie == "COTISATION" and user:

        membership, _ = Membership.objects.get_or_create(user=user)

        today = timezone.now().date()

        base_date = (
            membership.date_expiration
            if membership.date_expiration and membership.date_expiration > today
            else today
        )

        membership.date_activation = today
        membership.date_expiration = base_date + timedelta(days=365)

        membership.statut = "VALIDE"
    
        membership.save(
            update_fields=[
                "date_activation",
                "date_expiration",
                "statut"
            ]
        )

        return

    # =========================
    # ENROLEMENT ORGANISATION
    # =========================
    if transaction.categorie == "ENROLEMENT_ORG":

        organization = transaction.organization
        if not organization:
            return

        organization.est_affilie = True
        organization.date_affiliation = timezone.now().date()
        organization.save(
            update_fields=["est_affilie", "date_affiliation"]
        )

        return
    # =========================
    # COTISATION ORGANISATION
    # =========================
    if transaction.categorie == "COTISATION_ORG":

        organization = transaction.organization
        if not organization:
            return

        today = timezone.now().date()

        # renouvellement intelligent
        if organization.date_expiration and organization.date_expiration > today:
            base_date = organization.date_expiration
        else:
            base_date = today

        organization.date_activation = today
        organization.date_expiration = base_date + timedelta(days=365)

        organization.est_affilie = True

        organization.save(
            update_fields=[
                "date_activation",
                "date_expiration",
                "est_affilie",
            ]
        )

        return

# =====================================================
# SERVICE TRESORERIE
# =====================================================
class TresorerieService:

    @staticmethod
    def enregistrer_paiement(user, data):

        data.setdefault(
            "date_transaction",
            timezone.now().date()
        )

        transaction = Transaction.objects.create(
            **data,
            cree_par=user,
            statut="VALIDEE",
        )

        appliquer_transaction(transaction)

        return transaction

    # -------------------------------------------------
    # ENROLEMENT ORGANISATION (VMP-001 SIMPLE)
    # -------------------------------------------------
    @staticmethod
    def enroller_organisation(
        user,
        organization,
        montant_enrolement,
        montant_cotisation=None,
        description=""
    ):

        # sécurité basique
        if organization.est_affilie:
            raise ValueError("Adhésion déjà payée. Utilisez plutôt la cotisation annuelle.")

        with db_transaction.atomic():

            # 1️⃣ enrôlement
            t1 = Transaction.objects.create(
                type_transaction="ENTREE",
                categorie="ENROLEMENT_ORG",
                organization=organization,
                montant=int(montant_enrolement),
                description=description,
                statut="VALIDEE",
                cree_par=user,
            )

            appliquer_transaction(t1)

            # 2️⃣ cotisation optionnelle
            if montant_cotisation:
                t2 = Transaction.objects.create(
                    type_transaction="ENTREE",
                    categorie="COTISATION_ORG",
                    organization=organization,
                    montant=int(montant_cotisation),
                    description="Cotisation annuelle",
                    statut="VALIDEE",
                    cree_par=user,
                )

                appliquer_transaction(t2)

    @staticmethod
    def cotisation_organisation(
        user,
        organization,
        montant,
        description=""
    ):

        from .services import appliquer_transaction

        t = Transaction.objects.create(
            type_transaction="ENTREE",
            categorie="COTISATION_ORG",
            organization=organization,
            montant=int(montant),
            description=description or "Cotisation annuelle",
            statut="VALIDEE",
            cree_par=user,
        )

        appliquer_transaction(t)

        return t
    # -------------------------------------------------
    # SOLDE GLOBAL
    # -------------------------------------------------
    @staticmethod
    def get_solde():

        entrees = (
            Transaction.objects.filter(
                type_transaction="ENTREE",
                statut="VALIDEE"
            ).aggregate(total=Sum("montant"))["total"] or 0
        )

        sorties = (
            Transaction.objects.filter(
                type_transaction="SORTIE",
                statut="VALIDEE"
            ).aggregate(total=Sum("montant"))["total"] or 0
        )

        return entrees - sorties