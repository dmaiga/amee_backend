# roster/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.utils import timezone

from portals.models import Notification
from django.urls import reverse

# =====================================================
# DOSSIER CONSULTANT AMEE (VALIDATION INTERNE)
# =====================================================

class ConsultantProfile(models.Model):

    STATUT_CHOICES = (
        ("BROUILLON", "Brouillon"),
        ("SOUMIS", "Soumis"),
        ("VALIDE", "Validé"),
        ("REFUSE", "Refusé"),
    )

    STATUT_EMPLOI = (
        ("RECHERCHE", "Recherche active"),
        ("OUVERT", "Ouvert opportunités"),
        ("INDISPONIBLE", "Indisponible"),
    )

    SENIORITE = (
        ("JUNIOR", "Junior"),
        ("CONFIRME", "Confirmé"),
        ("SENIOR", "Senior"),
        ("EXPERT", "Expert"),
    )

 

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profil_roster"
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="BROUILLON"
    )

  
    # ================= POSITIONNEMENT =================
    titre_professionnel = models.CharField(max_length=255)
    resume_public = models.TextField()

    niveau_seniorite = models.CharField(
        max_length=20,
        choices=SENIORITE,
        blank=True
    )



    # ================= EXPERTISE =================

    annees_experience_ees = models.PositiveIntegerField(null=True, blank=True)
    secteurs_experience = models.TextField(blank=True)

    langues = models.CharField(max_length=255, blank=True)
    
    domaines_expertise = models.CharField(max_length=500)
    experience_geographique = models.TextField(blank=True)
    certifications = models.TextField(blank=True)
    attestations = models.TextField(
        blank=True,
        help_text="Certifications Banque mondiale, IFC, ISO..."
    )



    # ================= DOCUMENTS =================

    cv_public = models.FileField(
        upload_to="roster/public_cv/",
        null=True,
        blank=True
    )
    cv_document = models.FileField(
        upload_to="roster/cv_evaluation/",
        null=True,
        blank=True
    )

    lien_cv = models.CharField(blank=True)
    lien_linkedin = models.CharField(blank=True)

    # ================= DISPONIBILITE =================

    statut_professionnel = models.CharField(
        max_length=20,
        choices=STATUT_EMPLOI,
        blank=True
    )

    consentement_publication = models.BooleanField(default=True)

    mis_a_jour_le = models.DateTimeField(auto_now=True)


    # ==========================
    # VALIDATION BUREAU
    # ==========================

    eligibilite_validee = models.BooleanField(default=False)

    notes_interne_bureau = models.TextField(blank=True)

    valide_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="consultants_valides"
    )

    date_validation = models.DateTimeField(null=True, blank=True)

    motif_refus = models.TextField(null=True, blank=True)
    motif_reexamen = models.TextField(null=True, blank=True)

    est_disponible = models.BooleanField(default=True)

    cree_le = models.DateTimeField(auto_now_add=True)

    # ==========================
    # VALIDATION METIER
    # ==========================
 

    # ==========================
    # ETAT ACTIF
    # ==========================

    @property
    def est_actif_roster(self):

        if self.statut != "VALIDE":
            return False

        if not self.est_disponible:
            return False

        if not hasattr(self.user, "membership"):
            return False

        if not self.user.membership.est_actif:
            return False

        if self.user.statut_qualite in ["BANNI", "SUSPENDU"]:
            return False

        return True

    def __str__(self):
        return f"{self.user.email} - {self.statut}"
    


    def valider(self, validateur):

        ancien = self.statut

        self.statut = "VALIDE"
        self.valide_par = validateur
        self.date_validation = timezone.now()
        self.save()
        Notification.objects.create(
            user=self.user,
            type="ROSTER_VALIDE",
            message="Votre profil expert a été validé.",
            url=reverse("member_profile")
        )


        user = self.user
        if user.role != "CONSULTANT":
            user.role = "CONSULTANT"
            user.save(update_fields=["role"])

        # historique décision
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
        Notification.objects.create(
            user=self.user,
            type="ROSTER_REFUSE",
            message="Votre demande d'inscription au roster a été refusée.",
            url=reverse("roster_profile")
        )
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