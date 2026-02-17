# memberships/tests.py
import pytest


@pytest.mark.django_db
def test_membership_becomes_active(membre_actif):

    assert membre_actif.adhesion.est_actif is True
    assert membre_actif.id_membre_association is not None
