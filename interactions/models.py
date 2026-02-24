# interactions/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone


class ContactRequest(models.Model):

    STATUT_CHOICES = (
        ('ENVOYE', 'Demande envoyée'),
        ('MISSION_CONFIRME', 'Mission confirmée'),
        ('MISSION_TERMINEE', 'Mission terminée'),
        ('SANS_SUITE', 'Sans suite'),
        ('REFUSE', 'Refus du consultant'),
    )

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='demandes_clients'
    )

    consultant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='demandes_consultant'
    )

    mission = models.ForeignKey(
        'missions.Mission',
        on_delete=models.CASCADE,
        related_name='contacts'
    )

    est_collaboration_validee = models.BooleanField(
        default=False,
        help_text="Indique qu'une collaboration réelle a été confirmée"
    )

    message = models.TextField(blank=True, null=True)

    duree_estimee_jours = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    statut = models.CharField(
        max_length=30,
        choices=STATUT_CHOICES,
        default='ENVOYE'
    )

    date_derniere_relance = models.DateTimeField(
        null=True,
        blank=True
    )
    nb_relances = models.PositiveIntegerField(default=0)
    cree_le = models.DateTimeField(auto_now_add=True)

    date_suivi_prevu = models.DateTimeField(null=True, blank=True)
    suivi_envoye = models.BooleanField(default=False)

    suivi_effectue = models.BooleanField(default=False)
    date_suivi_reel = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.client} → {self.consultant} ({self.statut})"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['mission', 'consultant'],
                name='unique_contact_per_mission_consultant'
            )
        ]
        
    def save(self, *args, **kwargs):

        if self.statut == 'MISSION_CONFIRME':
            self.est_collaboration_validee = True

        super().save(*args, **kwargs)

    @property
    def etat_feedback(self):
    
        if self.statut != "MISSION_TERMINEE":
            return None
    
        if not hasattr(self, "feedback"):
            return "ATTENTE_FEEDBACK"
    
        if self.feedback.incident_signale:
            return "INCIDENT"
    
        return "OK"
    
    def terminer(self):
    
        if self.statut != "MISSION_CONFIRME":
            raise ValueError("Mission non active")
    
        self.statut = "MISSION_TERMINEE"
        self.save()
    
        self.mission.statut = "FERMEE"
        self.mission.save()
        
        