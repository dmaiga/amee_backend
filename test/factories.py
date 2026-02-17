from datetime import date
from tresorerie.models import Transaction


def payer_adhesion(email):

    return Transaction.objects.create(
        type_transaction="ENTREE",
        categorie="ADHESION",
        email_payeur=email,
        montant=5000,
        date_transaction=date.today(),
        statut="VALIDEE",
    )


def payer_cotisation(user):

    return Transaction.objects.create(
        type_transaction="ENTREE",
        categorie="COTISATION",
        membre=user,
        montant=10000,
        date_transaction=date.today(),
        statut="VALIDEE",
    )
