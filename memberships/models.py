# memberships/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
    
from django.utils.text import slugify
import os


def member_avatar_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{slugify(instance.user.email)}.{ext}"
    return os.path.join("avatars/members/", filename)


User = get_user_model()

from django.utils import timezone

class Membership(models.Model):

    ELIGIBILITE = (
        ("OPTION1", "Env/Social + 2 ans"),
        ("OPTION2", "Autre domaine + 5 ans"),
    )

    STATUT = (
        ("EN_ATTENTE", "En attente"),
        ("VALIDE", "Validé"),
        ("REFUSE", "Refusé"),
    )

    DIPLOME_NIVEAU = (
        ("LICENCE", "Licence"),
        ("MASTER", "Master"),
        ("DOCTORAT", "Doctorat"),
        ("AUTRE", "Autre"),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="membership"
    )

    # ===== ELIGIBILITE =====
    eligibilite_option = models.CharField(max_length=20, choices=ELIGIBILITE)

    cv_document = models.FileField(
        upload_to="adhesion/cv/",
        null=True,
        blank=True
    )

    diplome_niveau = models.CharField(
        max_length=20,
        choices=DIPLOME_NIVEAU,
        null=True,
        blank=True
    )

    diplome_intitule = models.CharField(
        max_length=255,
        blank=True
    )
    
    annee_diplome = models.CharField(
        max_length=255,
        blank=True
    )

    diplome_document = models.FileField(
        upload_to="adhesion/diplomes/",
        null=True,
        blank=True
    )
    
    # décision bureau
    
    statut = models.CharField(
        max_length=20,
        choices=STATUT,
        default="EN_ATTENTE"
    )

    valide_par = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="adhesions_validation"
    )
    motif_refus = models.TextField(blank=True)
    date_activation = models.DateField(null=True, blank=True)
    date_expiration = models.DateField(null=True, blank=True)

    cree_le = models.DateTimeField(auto_now_add=True)

    # ===============================
    # SOURCE DE VÉRITÉ
    # ===============================
    @property
    def est_actif(self):
        if not self.date_expiration:
            return False
        return self.date_expiration >= timezone.now().date()
  
    @property
    def est_membre_actif(self):
        return self.statut == "VALIDE" and self.est_actif  
  
    from datetime import date
    
    @property
    def jours_restants(self):
        if not self.date_expiration:
            return None
    
        delta = self.date_expiration - timezone.now().date()
        return delta.days

    def __str__(self):
        return f"{self.user.email} - actif:{self.est_actif}"

    @property
    def dernier_validateur(self):
    
        transaction = self.user.transactions.filter(
            statut="VALIDEE",
            categorie="COTISATION"
        ).order_by("-date_transaction").first()
    
        return transaction.cree_par if transaction else None

