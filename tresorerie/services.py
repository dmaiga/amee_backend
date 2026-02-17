# tresorerie/services.py

from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.db import transaction as db_transaction, IntegrityError
from memberships.models import Membership
import secrets

User = get_user_model()


# =====================================================
# OUTILS
# =====================================================

def generate_temp_password():
    return secrets.token_urlsafe(8)


def generate_member_id():
    """
    Génère un ID membre sûr :
    MEM-2026-001
    Basé sur le dernier ID existant (PAS de COUNT).
    """
    year = timezone.now().year

    last_user = (
        User.objects
        .filter(id_membre_association__startswith=f"MEM-{year}-")
        .order_by("-id_membre_association")
        .first()
    )

    if not last_user or not last_user.id_membre_association:
        next_number = 1
    else:
        last_number = int(last_user.id_membre_association.split("-")[-1])
        next_number = last_number + 1

    return f"MEM-{year}-{next_number:03d}"


# =====================================================
# CREATION MEMBRE (ADHESION)
# =====================================================

def handle_adhesion(transaction):

    if not transaction.email_payeur:
        return

    email = transaction.email_payeur.lower().strip()

    # -----------------------------
    # Recherche utilisateur
    # -----------------------------
    user = User.objects.filter(email=email).first()

    created = False
    temp_password = None

    if not user:
        #temp_password = generate_temp_password()
        temp_password = "temp123"

        user = User.objects.create_user(
            email=email,
            password=temp_password,
            first_name="",
            last_name="",
            role="MEMBER",
        )
        created = True

    # -----------------------------
    # Création membership
    # -----------------------------
    Membership.objects.get_or_create(user=user)

    # -----------------------------
    # 🔒 GENERATION ID MEMBRE SAFE
    # -----------------------------
    with db_transaction.atomic():

        locked_user = User.objects.select_for_update().get(pk=user.pk)

        if not locked_user.id_membre_association:

            # retry anti-collision UNIQUE
            for _ in range(5):
                try:
                    locked_user.id_membre_association = generate_member_id()
                    locked_user.role = "MEMBER"

                    locked_user.save(
                        update_fields=[
                            "id_membre_association",
                            "role"
                        ]
                    )
                    break

                except IntegrityError:
                    # un autre process a pris le même ID
                    continue

    # -----------------------------
    # Rattachement transaction
    # -----------------------------
    if not transaction.membre:
        transaction.membre = user
        transaction.save(update_fields=["membre"])

    # -----------------------------
    # Si cotisation déjà validée
    # -----------------------------
    cotisation = user.transactions.filter(
        type_transaction="ENTREE",
        categorie="COTISATION",
        statut="VALIDEE"
    ).order_by("-date_transaction").first()

    if cotisation and not user.adhesion.est_actif:
        handle_cotisation(cotisation)

    return user, created, temp_password


# =====================================================
# ACTIVATION / RENOUVELLEMENT
# =====================================================

def handle_cotisation(transaction):

    user = transaction.membre

    # fallback si adhésion créée après
    if not user and transaction.email_payeur:
        user = User.objects.filter(
            email=transaction.email_payeur.lower().strip()
        ).first()

        if user:
            transaction.membre = user
            transaction.save(update_fields=["membre"])

    if not user:
        return

    today = timezone.now().date()

    membership, _ = Membership.objects.get_or_create(user=user)

    # -----------------------------
    # Renouvellement intelligent
    # -----------------------------
    if membership.date_expiration and membership.date_expiration > today:
        base_date = membership.date_expiration
    else:
        base_date = today

    membership.date_activation = today
    membership.date_expiration = base_date + timedelta(days=365)

    membership.save(
        update_fields=[
            "date_activation",
            "date_expiration"
        ]
    )

    return membership


# =====================================================
# MOTEUR PRINCIPAL
# =====================================================

def process_membership_payment(transaction):
    """
    Déclenché automatiquement lors du passage
    BROUILLON → VALIDEE
    """

    if transaction.type_transaction != "ENTREE":
        return

    if transaction.categorie == "ADHESION":
        handle_adhesion(transaction)
        return

    if transaction.categorie == "COTISATION":
        handle_cotisation(transaction)
        return
