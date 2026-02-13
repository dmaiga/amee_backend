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

    def valider(self, validateur):
        self.statut = 'VALIDE'
        self.valide_par = validateur
        self.date_validation = timezone.now()
        self.save()

        # Promotion automatique MEMBER -> CONSULTANT
        self.user.role = 'CONSULTANT'
        self.user.save()
    
    def refuser(self, validateur, motif=None):

        self.statut = 'REFUSE'
        self.valide_par = validateur
        self.date_validation = timezone.now()
        self.motif_refus = motif
        self.save()

    def __str__(self):
        return f"{self.user.email} - {self.statut}"
