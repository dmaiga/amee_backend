#test/factories.py
from datetime import date
from tresorerie.models import Transaction


from datetime import date
from tresorerie.models import Transaction


def payer_adhesion(email):

    t = Transaction.objects.create(
        type_transaction="ENTREE",
        categorie="ADHESION",
        email_payeur=email,
        montant=5000,
        date_transaction=date.today(),
        statut="BROUILLON",
    )

    t.statut = "VALIDEE"
    t.save()

    return t


def payer_cotisation(user):

    t = Transaction.objects.create(
        type_transaction="ENTREE",
        categorie="COTISATION",
        membre=user,
        montant=10000,
        date_transaction=date.today(),
        statut="BROUILLON",
    )

    t.statut = "VALIDEE"
    t.save()

    return t
