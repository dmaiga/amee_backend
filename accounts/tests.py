from urllib import response
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
def test_login_jwt():

    user = User.objects.create_user(
        email="test@test.com",
        password="password123"
    )

    client = APIClient()

    response = client.post(
        "/api/auth/login/",
        {
            "email": "test@test.com",
            "password": "password123"
        },
        format="json"
    )

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data 
    print(response.status_code)
    print(response.data)
