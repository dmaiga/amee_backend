from django.db import models
from django.conf import settings


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

    cree_le = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback {self.note}/5"
  
    def save(self, *args, **kwargs):

        if self.contact_request.client != self.client:
            raise ValueError("Ce client ne correspond pas à la mission.")

        if self.contact_request.statut != "MISSION_TERMINEE":
            raise ValueError("Feedback autorisé uniquement après mission terminée.")

        super().save(*args, **kwargs)

class Signalement(models.Model):

    NIVEAU_CHOICES = (
        (1, "Premier signalement"),
        (2, "Avertissement"),
        (3, "Examen conseil"),
    )

    consultant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="signalements"
    )

    contact_request = models.ForeignKey(
        "interactions.ContactRequest",
        on_delete=models.CASCADE
    )

    niveau = models.PositiveSmallIntegerField(choices=NIVEAU_CHOICES)

    commentaire_interne = models.TextField()

    cree_le = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
        consultant = self.consultant
    
        if self.niveau == 1:
            consultant.statut_qualite = "SURVEILLANCE"
    
        elif self.niveau == 2:
            consultant.statut_qualite = "SUSPENDU"
    
        consultant.save()
    