# tresorerie/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from memberships.models import Membership
from django.utils import timezone
from datetime import timedelta
class Transaction(models.Model):

    TYPE_CHOICES = (
        ("ENTREE", "Entrée"),
        ("SORTIE", "Sortie"),
    )

    CATEGORIE_CHOICES = (
        ("ADHESION", "Frais d’adhésion"),
        ("COTISATION", "Cotisation annuelle"),

        ("DON", "Don"),
        ("SUBVENTION", "Subvention"),

        ("EVENEMENT", "Organisation événement"),
        ("FORMATION", "Formation"),
        ("ACHAT", "Acquisition matériel"),
        ("FONCTIONNEMENT", "Frais fonctionnement"),
    )

    STATUT_CHOICES = (
        ("BROUILLON", "Brouillon"),
        ("VALIDEE", "Validée"),
        ("ANNULEE", "Annulée"),
    )

    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default="BROUILLON")

    type_transaction = models.CharField(max_length=10, choices=TYPE_CHOICES)
    categorie = models.CharField(max_length=30, choices=CATEGORIE_CHOICES)
    montant = models.DecimalField(max_digits=12, decimal_places=0)

    description = models.TextField(blank=True)
    date_transaction = models.DateField()

    organization = models.ForeignKey(
        "organizations.Organization",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="transactions"
    )
    

    membre = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions",
        null=True,
        blank=True
    )


    email_payeur = models.EmailField(
        null=True,
        blank=True,
        help_text="Utilisé pour créer automatiquement un membre si inexistant"
    )

    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    cree_le = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.categorie} - {self.montant}"
    # =====================================================
    # MOTEUR MÉTIER MEMBERSHIP
    # =====================================================
    def save(self, *args, **kwargs):
    
        ancien_statut = None
    
        if self.pk:
            ancien_statut = (
                Transaction.objects
                .filter(pk=self.pk)
                .values_list("statut", flat=True)
                .first()
            )
    
        # sécurité métier
        if self.categorie == "ADHESION" and not self.email_payeur:
            raise ValueError("Une adhésion nécessite un email payeur.")
    
        super().save(*args, **kwargs)
    
        # Déclenche uniquement BROUILLON → VALIDEE
        if (
            self.statut == "VALIDEE"
            and ancien_statut == "BROUILLON"
        ):
            from .services import process_membership_payment
            process_membership_payment(self)
    