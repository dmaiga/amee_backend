from django.db import models
from accounts.models import User

class BoardMembership(models.Model):

    ROLE_BUREAU = (
        ("PRESIDENT", "Président"),
        ("SECRETAIRE", "Secrétaire"),
        ("COMPTABLE", "Comptable"),
        ("MEMBRE", "Membre du bureau"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    fonction = models.CharField(max_length=20, choices=ROLE_BUREAU)

    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)

    actif = models.BooleanField(default=True)