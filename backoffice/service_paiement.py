from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from tresorerie.services import TresorerieService

class PaiementService:

    @staticmethod
    @transaction.atomic
    def payer_membre(user, membre, operation, data):

        base_data = {
            "type_transaction": "ENTREE",
            "email_payeur": membre.email,
            "description": data.get("description"),
        }

        if operation in ["FULL", "ADHESION"]:
            montant = data.get("montant_adhesion") or 0
            if montant > 0:
                TresorerieService.enregistrer_paiement(
                    user=user,
                    data={**base_data,
                          "categorie": "ADHESION",
                          "montant": montant}
                )

        if operation in ["FULL", "COTISATION"]:
            montant = data.get("montant_cotisation") or 0
            if montant > 0:
                TresorerieService.enregistrer_paiement(
                    user=user,
                    data={**base_data,
                          "categorie": "COTISATION",
                          "montant": montant}
                )

    @staticmethod
    @transaction.atomic
    def payer_organisation(user, organisation, operation, montant, description):

        today = timezone.now().date()

        base_data = {
            "type_transaction": "ENTREE",
            "montant": montant,
            "description": description,
            "date_transaction": today,
            "organization": organisation,
        }

        if operation in ["FULL", "ADHESION"]:
            TresorerieService.enregistrer_paiement(
                user=user,
                data={**base_data, "categorie": "ADHESION"}
            )

            organisation.est_affilie = True
            organisation.date_affiliation = today
            organisation.date_expiration = today + timedelta(days=365)

        if operation in ["FULL", "COTISATION"]:
            TresorerieService.enregistrer_paiement(
                user=user,
                data={**base_data, "categorie": "COTISATION"}
            )

            base = organisation.date_expiration or today
            if base < today:
                base = today

            organisation.date_expiration = base + timedelta(days=365)

        organisation.save()