from django.db import models
from django.conf import settings
from django.utils import timezone


class ConsultantProfile(models.Model):

    STATUT_CHOICES = (
        ('BROUILLON', 'Brouillon'),
        ('SOUMIS', 'Soumis'),
        ('VALIDE', 'Validé'),
        ('REFUSE', 'Refusé'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profil_roster'
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='BROUILLON'
    )

    domaine_expertise = models.CharField(max_length=255)
    annees_experience = models.IntegerField()
    resume_profil = models.TextField()

    valide_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='profils_valides'
    )

    date_validation = models.DateTimeField(null=True, blank=True)

    cree_le = models.DateTimeField(auto_now_add=True)
    motif_refus = models.TextField(null=True, blank=True)
    est_disponible = models.BooleanField(default=True)
    
    class Meta:
        indexes = [
            models.Index(fields=["statut", "est_disponible"]),
        ]


    def valider(self, validateur):

        if not hasattr(self.user, "adhesion") or not self.user.adhesion.est_actif:
            raise ValueError("Impossible de valider un consultant non à jour.")

        self.statut = 'VALIDE'
        self.valide_par = validateur
        self.date_validation = timezone.now()
        self.save()

        # Promotion automatique
        self.user.role = 'CONSULTANT'
        self.user.save(update_fields=["role"])

    
    def refuser(self, validateur, motif=None):

        self.statut = 'REFUSE'
        self.valide_par = validateur
        self.date_validation = timezone.now()
        self.motif_refus = motif
        self.save()

    def __str__(self):
        return f"#{self.id}  - {self.user.email} - {self.statut}"

    @property
    def est_actif_roster(self):
        """
        Actif seulement si :
        - profil validé
        - disponible
        - membership actif
        """

        if self.statut != "VALIDE":
            return False

        if not self.est_disponible:
            return False

        if not hasattr(self.user, "adhesion"):
            return False

        return self.user.adhesion.est_actif
