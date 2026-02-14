# missions/models.py

from django.db import models
from django.conf import settings


class Mission(models.Model):

    STATUT_CHOICES = (
        ('OUVERTE', 'Ouverte'),
        ('FERMEE', 'Fermée'),
    )

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='missions'
    )

    titre = models.CharField(max_length=255)
    description = models.TextField()

    domaine = models.CharField(max_length=255)

    localisation = models.CharField(max_length=255, blank=True, null=True)

    duree_estimee_jours = models.PositiveIntegerField(null=True, blank=True)

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='OUVERTE'
    )

    cree_le = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre
