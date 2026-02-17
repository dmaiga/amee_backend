# missions/tests.py
import pytest
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


User = get_user_model()


@pytest.mark.django_db
def test_only_client_can_create_mission():

    client_api = APIClient()

    # utilisateur NON client
    user = User.objects.create_user(
        email="member@test.com",
        password="pass",
        role="MEMBER"
    )

    client_api.force_authenticate(user=user)

    response = client_api.post(
        "/api/missions/creer/",
        {
            "titre": "Mission test",
            "description": "desc",
            "domaine": "env",
        },
        format="json"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_client_can_create_mission(auth_client):

    response = auth_client.post(
        "/api/missions/creer/",
        {
            "titre": "Mission test",
            "description": "desc",
            "domaine": "env"
        },
        format="json"
    )

    assert response.status_code == 201
