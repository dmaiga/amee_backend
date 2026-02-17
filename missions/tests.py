import pytest


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
