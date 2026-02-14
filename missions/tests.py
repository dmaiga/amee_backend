import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

@pytest.mark.django_db
def test_create_mission(auth_client):

    response = auth_client.post(
        "/api/missions/creer/",
        {
            "titre": "Test mission",
            "description": "desc",
            "domaine": "env"
        },
        format="json"
    )

    assert response.status_code == 201
    assert response.data["titre"] == "Test mission"
    assert response.data["description"] == "desc"