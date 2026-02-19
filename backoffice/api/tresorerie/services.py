# backoffice/api/tresorerie/services.py

from django.utils import timezone
from django.db import transaction as db_transaction
from tresorerie.models import Transaction


class TresorerieService:

    @staticmethod
    @db_transaction.atomic
    def enregistrer_paiement(user, data):
        """
        Action métier COMPTA.

        Crée une transaction puis la valide immédiatement.
        Le moteur tresorerie déclenche ensuite automatiquement
        membership / activation si nécessaire.
        """

        transaction = Transaction.objects.create(
            type_transaction=data["type_transaction"],
            categorie=data["categorie"],
            montant=data["montant"],
            date_transaction=data.get(
                "date_transaction",
                timezone.now().date()
            ),
            description=data.get("description", ""),
            email_payeur=data.get("email_payeur"),
            membre_id=data.get("membre_id"),
            cree_par=user,
            statut="BROUILLON",
        )

        # 🔥 ÉVÉNEMENT MÉTIER
        transaction.statut = "VALIDEE"
        transaction.save()

        return transaction
