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

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='adhesion'
    )

    date_activation = models.DateField(null=True, blank=True)
    date_expiration = models.DateField(null=True, blank=True)

    valide_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='adhesions_validees'
    )

    cree_le = models.DateTimeField(auto_now_add=True)

    # ===============================
    # SOURCE DE VÉRITÉ
    # ===============================
    @property
    def est_actif(self):
        if not self.date_expiration:
            return False
        return self.date_expiration >= timezone.now().date()
    

    def __str__(self):
        return f"{self.user.email} - actif:{self.est_actif}"

    @property
    def dernier_validateur(self):
    
        transaction = self.user.transactions.filter(
            statut="VALIDEE",
            categorie="COTISATION"
        ).order_by("-date_transaction").first()
    
        return transaction.cree_par if transaction else None


class MemberProfile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="member_profile"
    )

    photo = models.ImageField(
        upload_to=member_avatar_path,
        null=True,
        blank=True
    )

    telephone = models.CharField(max_length=30, blank=True)
 
    fonction = models.CharField(max_length=255, blank=True)
    secteur = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)

    mis_a_jour_le = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.user.email