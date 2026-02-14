import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def auth_client(db):

    user = User.objects.create_user(
        email="client@test.com",
        password="pass123"
    )

    client = APIClient()

    response = client.post(
        "/api/auth/login/",
        {
            "email": "client@test.com",
            "password": "pass123"
        }
    )

    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
    )

    return client
