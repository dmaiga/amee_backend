#tresorerie/tests.py
import pytest
from datetime import date
from django.contrib.auth import get_user_model
from tresorerie.models import Transaction

User = get_user_model()


@pytest.mark.django_db
def test_adhesion_creates_member():

    t = Transaction.objects.create(
        type_transaction="ENTREE",
        categorie="ADHESION",
        email_payeur="expert@test.com",
        montant=5000,
        date_transaction=date.today(),
        statut="BROUILLON",
    )

    # validation comptable réelle
    t.statut = "VALIDEE"
    t.save()

    user = t.membre
    user.refresh_from_db() 
    assert user is not None
    assert user.id_membre_association is not None


@pytest.mark.django_db
def test_cotisation_before_adhesion():

    user = User.objects.create_user(
        email="reverse@test.com",
        password="x"
    )

    # COTISATION d'abord
    cotisation = Transaction.objects.create(
        type_transaction="ENTREE",
        categorie="COTISATION",
        membre=user,
        montant=10000,
        date_transaction=date.today(),
        statut="BROUILLON",
    )

    cotisation.statut = "VALIDEE"
    cotisation.save()

    # ADHESION ensuite
    adhesion = Transaction.objects.create(
        type_transaction="ENTREE",
        categorie="ADHESION",
        email_payeur=user.email,
        montant=5000,
        date_transaction=date.today(),
        statut="BROUILLON",
    )

    adhesion.statut = "VALIDEE"
    adhesion.save()

    user.refresh_from_db()

    assert user.adhesion.est_actif is True
