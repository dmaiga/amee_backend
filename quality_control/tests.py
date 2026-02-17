import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from missions.models import Mission
from interactions.models import ContactRequest

User = get_user_model()


@pytest.mark.django_db
def test_feedback_creates_incident(membre_actif):

    api = APIClient()

    # ✅ vrai client propriétaire
    client = User.objects.create_user(
        email="client2@test.com",
        password="x",
        role="CLIENT"
    )

    api.force_authenticate(user=client)

    mission = Mission.objects.create(
        titre="Mission",
        description="desc",
        domaine="env",
        client=client
    )

    # ✅ mission terminée (condition obligatoire métier)
    contact = ContactRequest.objects.create(
        client=client,
        consultant=membre_actif,
        mission=mission,
        statut="MISSION_TERMINEE"
    )
    response = api.post(
        f"/api/quality/feedback/{contact.id}/",
        {
            "note": 2,
            "commentaire": "Problème sérieux",
            "incident_signale": True,
            "description_incident": "Problème sérieux"
        },
        format="json"
    )
    

    assert response.status_code == 201
