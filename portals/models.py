# clients/models.py

from django.db import models
from django.conf import settings

class ClientProfile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_profile"
    )
    statut_onboarding = models.CharField(
        max_length=20,
        choices=[
            ("AUTO", "Auto validé"),
            ("EN_ATTENTE", "En attente"),
            ("VALIDE", "Validé"),
            ("REFUSE", "Refusé"),
        ],
        default="EN_ATTENTE"
    )
    nom_entreprise = models.CharField(max_length=255)
    secteur_activite = models.CharField(max_length=255)

    email_pro = models.EmailField(unique=True)
    telephone_pro = models.CharField(max_length=50, blank=True)

    nom_contact = models.CharField(max_length=255)
    fonction_contact = models.CharField(max_length=255, blank=True)

    est_verifie = models.BooleanField(default=False)
    valide_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="clients_valides"
    )

    cree_le = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom_entreprise
    

