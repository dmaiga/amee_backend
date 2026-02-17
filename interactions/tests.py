import pytest
from django.utils import timezone
from datetime import timedelta

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from missions.models import Mission
from interactions.models import ContactRequest
from roster.models import ConsultantProfile

User = get_user_model()



@pytest.mark.django_db
def test_client_request_contact(auth_client, membre_actif):

    consultant = membre_actif
    consultant.role = "CONSULTANT"
    consultant.save()

    # ✅ le consultant doit exister dans le roster et être VALIDÉ
    ConsultantProfile.objects.create(
        user=consultant,
        domaine_expertise="Data",
        annees_experience=10,
        resume_profil="Senior",
        statut="VALIDE",
        est_disponible=True,
    )

    mission = Mission.objects.create(
        titre="Mission test",
        description="desc",
        domaine="env",
        client=auth_client.handler._force_user
    )

    response = auth_client.post(
        "/api/interactions/request-contact/",
        {
            "mission": mission.id,
            "consultant": consultant.id
        },
        format="json"
    )

    assert response.status_code == 201


@pytest.mark.django_db
def test_consultant_accepts_contact(membre_actif):

    api = APIClient()

    consultant = membre_actif
    consultant.role = "CONSULTANT"
    consultant.save()

    client = User.objects.create_user(
        email="client@test.com",
        password="x",
        role="CLIENT"
    )

    mission = Mission.objects.create(
        titre="Mission",
        description="desc",
        domaine="env",
        client=client
    )

    contact = ContactRequest.objects.create(
        client=client,
        consultant=consultant,
        mission=mission
    )

    api.force_authenticate(user=consultant)

    response = api.patch(
        f"/api/interactions/{contact.id}/update-status/",
        {"statut": "MISSION_CONFIRME"},
        format="json"
    )

    contact.refresh_from_db()

    assert response.status_code == 200
    assert contact.statut == "MISSION_CONFIRME"


@pytest.mark.django_db
def test_consultant_confirms_mission_done(membre_actif):

    api = APIClient()

    consultant = membre_actif
    consultant.role = "CONSULTANT"
    consultant.save()

    client = User.objects.create_user(
        email="client@test.com",
        password="x",
        role="CLIENT"
    )

    mission = Mission.objects.create(
        titre="Mission",
        description="desc",
        domaine="env",
        client=client
    )

    contact = ContactRequest.objects.create(
        client=client,
        consultant=consultant,
        mission=mission,
        statut="MISSION_CONFIRME"
    )

    api.force_authenticate(user=consultant)

    response = api.patch(
        f"/api/interactions/{contact.id}/terminer-mission/"
    )

    contact.refresh_from_db()
    mission.refresh_from_db()

    assert response.status_code == 200
    assert contact.statut == "MISSION_TERMINEE"
    assert mission.statut == "FERMEE"
