from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from roster.models import ConsultantProfile

User = get_user_model()


@receiver(post_save, sender=User)
def sync_consultant_availability(sender, instance, **kwargs):

    # seulement consultants
    if instance.role != "CONSULTANT":
        return

    try:
        profil = instance.profil_roster
    except ConsultantProfile.DoesNotExist:
        return

    # 🔥 suspension automatique
    if instance.statut_qualite in ["SUSPENDU", "BANNI"]:
        if profil.est_disponible:
            profil.est_disponible = False
            profil.save(update_fields=["est_disponible"])
