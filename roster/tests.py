#roster/tests.py
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
def test_roster_requires_active_membership(membre_actif):

    client = APIClient()
    client.force_authenticate(user=membre_actif)

    response = client.post(
        "/api/roster/soumettre/",
        {
            "domaine_expertise": "Env",
            "annees_experience": 10,
            "resume_profil": "Expert"
        },
        format="json"
    )

    assert response.status_code == 201


@pytest.mark.django_db
def test_roster_blocked_without_payment():

    user = User.objects.create_user(
        email="nopay@test.com",
        password="x"
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post("/api/roster/soumettre/", {})

    assert response.status_code == 403
