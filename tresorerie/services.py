from memberships.models import Membership
from tresorerie.models import Transaction
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

from django.db.models import Sum
from tresorerie.models import Transaction
import secrets

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

from django.core.mail import send_mail
from django.conf import settings


def envoyer_email_enrolement(user, password_temporaire):

    sujet = "Bienvenue — Activation de votre compte membre"

    message = f"""
Bonjour {user.first_name or ''},

Votre adhésion a été enregistrée.

Vos identifiants :

Email : {user.email}
Mot de passe temporaire : {password_temporaire}

Veuillez vous connecter et modifier votre mot de passe.

Cordialement,
Administration
"""

    send_mail(
        sujet,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

User = get_user_model()

def appliquer_transaction(transaction):

    if transaction.type_transaction != "ENTREE":
        return

    user = transaction.membre

    if not user and transaction.email_payeur:
        user, _ = User.objects.get_or_create(
            email=transaction.email_payeur,
            defaults={"role": "MEMBER"}
        )
        transaction.membre = user
        transaction.save(update_fields=["membre"])

    if not user:
        return

    # -----------------------------
    # ADHESION = existence seulement
    # -----------------------------
    # -----------------------------
    # ADHESION = onboarding membre
    # -----------------------------
    if transaction.categorie == "ADHESION":
    
        membership, _ = Membership.objects.get_or_create(user=user)
    
        is_new_member = False
        temp_password = None
    
        # Création ID membre (sert de déclencheur onboarding)
        if not user.id_membre_association:
            user.id_membre_association = generate_member_id()
            is_new_member = True
    
        # password initial uniquement pour nouveau membre
        if is_new_member:
            temp_password = "changeMe"
            user.set_password(temp_password)
    
        # rôle garanti
        user.role = "MEMBER"
        user.save()
    
        # email envoyé UNE seule fois
        if is_new_member:
            envoyer_email_enrolement(user, temp_password)
    
        return
    
    # -----------------------------
    # COTISATION = ACTIVATION UNIQUE
    # -----------------------------
    if transaction.categorie == "COTISATION":

        membership, _ = Membership.objects.get_or_create(user=user)

        today = timezone.now().date()

        # renouvellement intelligent
        if membership.date_expiration and membership.date_expiration > today:
            base_date = membership.date_expiration
        else:
            base_date = today

        membership.date_activation = today
        membership.date_expiration = base_date + timedelta(days=365)

        membership.save(
            update_fields=["date_activation", "date_expiration"]
        )

class TresorerieService:

    @staticmethod
    def enregistrer_paiement(user, data):

        # ✅ garantir la date automatiquement
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



    # =====================================================
    # SOLDE GLOBAL
    # =====================================================
    @staticmethod
    def get_solde():
        """
        Calcule le solde réel de la trésorerie :
        Entrées - Sorties validées uniquement.
        """

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
    