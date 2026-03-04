# missions/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone

class Mission(models.Model):

    STATUT_CHOICES = (
    ("BROUILLON", "Brouillon"),
    ("ACTIVE", "Active"),
    ("TERMINEE", "Terminée"),
    ("ANNULEE", "Annulée"),
    )
    TYPE_PUBLICATION = (
        ("PUBLIQUE", "Mission publique"),
        ("CIBLEE", "Mission ciblée"),
    )

    type_publication = models.CharField(
        max_length=20,
        choices=TYPE_PUBLICATION,
        default="PUBLIQUE"
    )

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="missions"
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
    date_fin = models.DateField(null=True, blank=True)
    
    cree_le = models.DateTimeField(auto_now_add=True)
    publie_le = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.titre
    from django.utils import timezone

    @property
    def est_visible(self):
        if self.type_publication != "PUBLIQUE":
            return False
        if self.statut != "ACTIVE":
            return False
        if not self.publie_le:
            return False
        if self.date_fin and self.date_fin < timezone.now().date():
            return False
        return True

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

class MissionApplication(models.Model):
    STATUT_CHOICES = (
        ("EN_ATTENTE", "En attente"),
        ("RETENU", "Retenu"),
        ("REFUSE", "Refusé"),
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="EN_ATTENTE"
    )
    mission = models.ForeignKey(
        Mission,
        related_name="applications",
        on_delete=models.CASCADE
    )
    consultant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    message = models.TextField(blank=True)

    # dossier spécifique à cette mission
    proposition_technique = models.FileField(
        upload_to="applications/propositions/technique",
        null=True,
        blank=True
    )

    proposition_financiere = models.FileField(
        upload_to="applications/propositions/financiere",
        null=True,
        blank=True
    )
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("mission", "consultant")