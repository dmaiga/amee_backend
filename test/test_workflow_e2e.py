import pytest
from rest_framework.test import APIClient
from test.factories import payer_adhesion, payer_cotisation


@pytest.mark.django_db
def test_full_amee_flow():

    client = APIClient()

    adhesion = payer_adhesion("flow@test.com")
    user = adhesion.membre
    
    payer_cotisation(user)
    
    user.refresh_from_db()
    
    client.force_authenticate(user=user)
    
    response = client.post(
        "/api/roster/soumettre/",
        {
            "domaine_expertise": "Data",
            "annees_experience": 8,
            "resume_profil": "Senior"
        },
        format="json"
    )

    assert response.status_code == 201
