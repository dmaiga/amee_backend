# roster/tests.py

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from roster.models import ConsultantProfile, ConsultantPublicProfile

User = get_user_model()


# =====================================================
# FIXTURE CLIENT API
# =====================================================

@pytest.fixture
def api_client():
    return APIClient()


# =====================================================
# TEST — SOUMISSION AVEC ADHÉSION ACTIVE
# =====================================================

@pytest.mark.django_db
def test_roster_submission_requires_active_membership(
    api_client,
    membre_actif
):
    """
    Un membre avec cotisation active
    peut soumettre une candidature roster.
    """

    api_client.force_authenticate(user=membre_actif)

    payload = {
        "domaine_expertise": "Environnement",
        "annees_experience": 10,
        "resume_public": "Expert EIES avec expérience régionale"
    }

    response = api_client.post(
        "/api/roster/soumettre/",
        payload,
        format="json"
    )

    assert response.status_code == 201

    # profil créé
    profil = ConsultantProfile.objects.get(user=membre_actif)
    assert profil.statut == "SOUMIS"

    # public profile créé automatiquement
    assert hasattr(profil, "public_profile")
    assert profil.public_profile.resume_public != ""


# =====================================================
# TEST — BLOQUÉ SANS ADHÉSION
# =====================================================

@pytest.mark.django_db
def test_roster_blocked_without_membership(api_client):

    user = User.objects.create_user(
        email="nopay@test.com",
        password="test123"
    )

    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/roster/soumettre/",
        {
            "domaine_expertise": "Env",
            "annees_experience": 5,
            "resume_public": "Profil test"
        },
        format="json"
    )

    assert response.status_code == 403

    assert ConsultantProfile.objects.count() == 0


# =====================================================
# TEST — REDEMANDE APRÈS REFUS
# =====================================================

@pytest.mark.django_db
def test_resubmission_after_refusal(api_client, membre_actif):

    api_client.force_authenticate(user=membre_actif)

    profil = ConsultantProfile.objects.create(
        user=membre_actif,
        statut="REFUSE",
        domaine_expertise="Env",
        annees_experience=8,
    )

    response = api_client.post(
        "/api/roster/soumettre/",
        {"motif": "Profil mis à jour"},
        format="json"
    )

    assert response.status_code == 200

    profil.refresh_from_db()
    assert profil.statut == "SOUMIS"
    assert profil.motif_refus is None


# =====================================================
# TEST — LISTE PUBLIQUE FILTRÉE
# =====================================================

@pytest.mark.django_db
def test_public_roster_visibility(api_client, membre_actif):

    profil = ConsultantProfile.objects.create(
        user=membre_actif,
        statut="VALIDE",
        domaine_expertise="Env",
        annees_experience=12,
        est_disponible=True
    )

    ConsultantPublicProfile.objects.create(
        consultant=profil,
        resume_public="Expert senior",
        consentement_publication=True
    )

    response = api_client.get("/api/roster/public/")

    assert response.status_code == 200
    assert len(response.data) == 1


# =====================================================
# TEST — NON VISIBLE SANS CONSENTEMENT
# =====================================================

@pytest.mark.django_db
def test_public_profile_requires_consent(api_client, membre_actif):

    profil = ConsultantProfile.objects.create(
        user=membre_actif,
        statut="VALIDE",
        domaine_expertise="Env",
        annees_experience=12,
        est_disponible=True
    )

    ConsultantPublicProfile.objects.create(
        consultant=profil,
        resume_public="Expert senior",
        consentement_publication=False
    )

    response = api_client.get("/api/roster/public/")

    assert response.status_code == 200
    assert len(response.data) == 0