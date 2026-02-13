# memberships/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
User = get_user_model()


class Membership(models.Model):

    STATUT_CHOICES = (
        ('EN_ATTENTE', 'En attente de paiement'),
        ('ACTIF', 'Actif'),
        ('EXPIRE', 'Expiré'),
        ('SUSPENDU', 'Suspendu'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='adhesion'
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='EN_ATTENTE'
    )

    montant_paye = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0,
        help_text="Montant en FCFA"
    )

    date_paiement = models.DateField(null=True, blank=True)
    date_expiration = models.DateField(null=True, blank=True)

    valide_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='adhesions_validees'
    )

    cree_le = models.DateTimeField(auto_now_add=True)

    # -----------------------------------------
    # PROPRIÉTÉ MÉTIER
    # -----------------------------------------

    @property
    def est_actif(self):
        if self.statut != 'ACTIF' or not self.date_expiration:
            return False
        return self.date_expiration >= timezone.now().date()

    # -----------------------------------------
    # ACTIVATION OFFICIELLE
    # -----------------------------------------

    def activer(self, valide_par, duree_jours=365):
        """
        Activation officielle :
        - Génère ID MEM-YYYY-XXX si inexistant
        - Promeut CLIENT -> MEMBER
        - Définit validité annuelle
        """

        # Génération ID UNIQUEMENT si pas encore membre
        if not self.user.id_membre_association:

            annee = timezone.now().year

            compteur = User.objects.filter(
                id_membre_association__startswith=f"MEM-{annee}"
            ).count()


            nouvel_id = f"MEM-{annee}-{compteur + 1:03d}"

            self.user.id_membre_association = nouvel_id

        # Promotion rôle
        self.user.role = 'MEMBER'
        self.user.save()

        # Mise à jour adhésion
        self.statut = 'ACTIF'
        self.date_paiement = timezone.now().date()
        self.date_expiration = self.date_paiement + timedelta(days=duree_jours)
        self.valide_par = valide_par

        self.save()

    def __str__(self):
        return f"{self.user.email} - {self.statut}"
