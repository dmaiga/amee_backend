# missions/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone

class Mission(models.Model):

    STATUT_CHOICES = (
        ("ACTIVE", "Active"),
        ("TERMINEE", "Terminée"),
    )

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="missions"
    )
    expert_cible = models.ForeignKey(
        "accounts.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="missions_proposees"
    )
    titre = models.CharField(max_length=255)

    description = models.TextField(
        help_text="Contexte général"
    )

    objectifs = models.TextField(blank=True)
    livrables_attendus = models.TextField(blank=True)

    domaine = models.CharField(max_length=255)

    localisation = models.CharField(max_length=255, blank=True, null=True)

    duree_estimee_jours = models.PositiveIntegerField(null=True, blank=True)

    budget_estime = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="ACTIVE"
    )

    cree_le = models.DateTimeField(auto_now_add=True)
    publie_le = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.titre


class MissionDocument(models.Model):

    TYPE_DOC = (
        ("TOR", "Termes de référence"),
        ("CDC", "Cahier des charges"),
        ("ANNEXE", "Annexe technique"),
        ("AUTRE", "Autre"),
    )

    mission = models.ForeignKey(
        Mission,
        on_delete=models.CASCADE,
        related_name="documents"
    )

    type_document = models.CharField(
        max_length=20,
        choices=TYPE_DOC
    )

    fichier = models.FileField(
        upload_to="missions/documents/"
    )

    nom = models.CharField(max_length=255)

    upload_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    cree_le = models.DateTimeField(auto_now_add=True)

