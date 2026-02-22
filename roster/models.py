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

    # -------- Infos minimales AMEE --------
    domaine_expertise = models.CharField(max_length=255)
    annees_experience = models.IntegerField()

    cv_document = models.FileField(
        upload_to="roster/cv/",
        null=True,
        blank=True
    )

    eligibilite_option = models.CharField(
        max_length=20,
        choices=(
            ("OPTION1", "Diplôme + expérience"),
            ("OPTION2", "Expérience validée conseil"),
        ),
        null=True,
        blank=True
    )

    notes_interne_bureau = models.TextField(blank=True)

    # -------- décision --------
    valide_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    date_validation = models.DateTimeField(null=True, blank=True)

    cree_le = models.DateTimeField(auto_now_add=True)

    est_disponible = models.BooleanField(default=True)
    motif_refus = models.TextField(null=True, blank=True)
    motif_reexamen = models.TextField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["statut", "est_disponible"]),
        ]
    

    @property
    def est_actif_roster(self):

        if self.statut != "VALIDE":
            return False

        if not self.est_disponible:
            return False

        if not hasattr(self.user, "adhesion"):
            return False

        if not self.user.adhesion.est_actif:
            return False

        if self.user.statut_qualite in ["BANNI", "SUSPENDU"]:
            return False

        return True

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


class ConsultantPublicProfile(models.Model):

    consultant = models.OneToOneField(
        ConsultantProfile,
        on_delete=models.CASCADE,
        related_name="public_profile"
    )

    resume_public = models.TextField()

    langues = models.CharField(max_length=255, blank=True)

    secteurs_experience = models.TextField(blank=True)
    experience_geographique = models.TextField(blank=True)

    lien_cv = models.URLField(blank=True)
    lien_linkedin = models.URLField(blank=True)

    STATUT_DISPO = (
        ("RECHERCHE", "Recherche active"),
        ("OUVERT", "Ouvert opportunités"),
        ("INDISPONIBLE", "Indisponible"),
    )

    statut_disponibilite = models.CharField(
        max_length=20,
        choices=STATUT_DISPO,
        default="OUVERT"
    )

    consentement_publication = models.BooleanField(default=False)

    mis_a_jour_le = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PublicProfile - {self.consultant.user.email}"
    
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