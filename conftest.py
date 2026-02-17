# conftest.py
import pytest
from datetime import date
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from tresorerie.models import Transaction
from missions.models import Mission
from interactions.models import ContactRequest

User = get_user_model()


# -----------------------------
# API CLIENT
# -----------------------------
@pytest.fixture
def api_client():
    return APIClient()


# -----------------------------
# CLIENT AUTHENTIFIÉ
# -----------------------------
@pytest.fixture
def auth_client(api_client):

    user = User.objects.create_user(
        email="client@test.com",
        password="pass123",
        role="CLIENT"
    )

    api_client.force_authenticate(user=user)
    return api_client


# -----------------------------
# MEMBRE ACTIF (piloté trésorerie)
# -----------------------------
@pytest.fixture
def membre_actif(db):

    email = "member@test.com"

    # ADHESION (événement comptable)
    adhesion = Transaction.objects.create(
        type_transaction="ENTREE",
        categorie="ADHESION",
        email_payeur=email,
        montant=5000,
        date_transaction=date.today(),
        statut="BROUILLON",
    )

    adhesion.statut = "VALIDEE"
    adhesion.save()

    user = adhesion.membre

    # COTISATION (événement comptable)
    cotisation = Transaction.objects.create(
        type_transaction="ENTREE",
        categorie="COTISATION",
        membre=user,
        montant=10000,
        date_transaction=date.today(),
        statut="BROUILLON",
    )

    cotisation.statut = "VALIDEE"
    cotisation.save()

    user.refresh_from_db()
    return user

# -----------------------------
# COLLABORATION (piloté interactions)
# -----------------------------

@pytest.fixture
def collaboration(api_client, membre_actif):

    client = User.objects.create_user(
        email="client2@test.com",
        password="x",
        role="CLIENT"
    )

    api_client.force_authenticate(user=client)

    mission = Mission.objects.create(
        titre="Mission",
        description="desc",
        domaine="env",
        client=client
    )

    contact = ContactRequest.objects.create(
        client=client,
        consultant=membre_actif,
        mission=mission,
        statut="MISSION_TERMINEE"
    )

    return contact, api_client
