# quality_control/models.py
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

    
class IncidentReview(models.Model):

    contact_request = models.OneToOneField(
        "interactions.ContactRequest",
        on_delete=models.CASCADE
    )

    consultant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    feedback = models.OneToOneField(
        "quality_control.Feedback",
        on_delete=models.CASCADE,
        related_name="incident"
    )

    statut = models.CharField(
        max_length=20,
        choices=(
            ("OUVERT", "Ouvert"),
            ("EN_ANALYSE", "En analyse"),
            ("CLOTURE", "Clôturé"),
        ),
        default="OUVERT"
    )

    cree_le = models.DateTimeField(auto_now_add=True)

    from django.db import transaction
    
    @transaction.atomic
    def creer_signalement(self, niveau, commentaire):
        from .models import Signalement

        if self.statut == "CLOTURE":
            raise ValueError("Cet incident est déjà clôturé.")

        if hasattr(self, "signalement"):
            raise ValueError("Un signalement existe déjà pour cet incident.")

        signalement = Signalement.objects.create(
            incident=self,
            consultant=self.consultant,
            niveau=niveau,
            commentaire_interne=commentaire,
        )

        # appliquer sanction automatiquement
        if niveau == 1:
            self.consultant.statut_qualite = "SURVEILLANCE"
        elif niveau == 2:
            self.consultant.statut_qualite = "SUSPENDU"

        self.consultant.save()

        self.statut = "CLOTURE"
        self.save()

        return signalement

class Feedback(models.Model):

    contact_request = models.OneToOneField(
        "interactions.ContactRequest",
        on_delete=models.CASCADE,
        related_name="feedback"
    )

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    note = models.PositiveIntegerField()
    commentaire = models.TextField(blank=True)
    incident_signale = models.BooleanField(default=False)
    description_incident = models.TextField(blank=True)

    cree_le = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback {self.note}/5"
  
    def save(self, *args, **kwargs):

        is_new = self.pk is None

        if self.contact_request.client != self.client:
            raise ValidationError("Ce client ne correspond pas à la mission.")

        if self.contact_request.statut != "MISSION_TERMINEE":
            raise ValidationError("Feedback autorisé uniquement après mission terminée.")

        super().save(*args, **kwargs)

        # créer incident seulement à la création
        if is_new and self.incident_signale:
            IncidentReview.objects.get_or_create(
                contact_request=self.contact_request,
                consultant=self.contact_request.consultant,
                feedback=self
            )

class Signalement(models.Model):

    incident = models.OneToOneField(
        "IncidentReview",
        on_delete=models.CASCADE,
        related_name="signalement"
    )

    consultant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    niveau = models.PositiveSmallIntegerField(
        choices=(
            (1, "Premier avertissement"),
            (2, "Suspension"),
            (3, "Examen conseil"),
        )
    )

    commentaire_interne = models.TextField()
    cree_le = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.incident_id:
            raise ValueError("Un signalement doit provenir d'un incident.")
        super().save(*args, **kwargs)
