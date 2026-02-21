# roster/models.py
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
    motif_reexamen = models.TextField(null=True, blank=True)

    est_disponible = models.BooleanField(default=True)
    
    class Meta:
        indexes = [
            models.Index(fields=["statut", "est_disponible"]),
        ]


    def valider(self, validateur):

        ancien = self.statut

        self.statut = "VALIDE"
        self.valide_par = validateur
        self.date_validation = timezone.now()
        self.save()

        RosterDecisionHistory.objects.create(
            profil=self,
            ancien_statut=ancien,
            nouveau_statut="VALIDE",
            decision_par=validateur
        )

    def refuser(self, validateur, motif=None):

        ancien = self.statut

        self.statut = "REFUSE"
        self.valide_par = validateur
        self.date_validation = timezone.now()
        self.motif_refus = motif
        self.save()

        RosterDecisionHistory.objects.create(
            profil=self,
            ancien_statut=ancien,
            nouveau_statut="REFUSE",
            motif=motif,
            decision_par=validateur
        )

    def demander_reexamen(self, demandeur, motif):
    
        if self.statut != "REFUSE":
            raise ValueError("Réexamen non autorisé.")
    
        ancien = self.statut
    
        self.statut = "SOUMIS"
        self.motif_reexamen = motif
        self.motif_refus = None
        self.save()
    
        RosterDecisionHistory.objects.create(
            profil=self,
            ancien_statut=ancien,
            nouveau_statut="SOUMIS",
            motif=motif,
            decision_par=demandeur
        )
    
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

class RosterDecisionHistory(models.Model):

    profil = models.ForeignKey(
        "ConsultantProfile",
        on_delete=models.CASCADE,
        related_name="historique"
    )

    ancien_statut = models.CharField(max_length=20)
    nouveau_statut = models.CharField(max_length=20)

    motif = models.TextField(blank=True, null=True)

    decision_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL
    )

    cree_le = models.DateTimeField(auto_now_add=True)