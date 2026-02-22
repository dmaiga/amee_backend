from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from interactions.models import ContactRequest

@receiver(post_save, sender=ContactRequest)
def envoyer_email_mise_en_relation(sender, instance, created, **kwargs):

    if created or instance.statut != "MISSION_CONFIRME":
        return

    client = instance.client
    consultant = instance.consultant
    mission = instance.mission

    message = f"""
Bonjour,

La mise en relation a été confirmée par AMEE.

MISSION
--------
Titre : {mission.titre}
Domaine : {mission.domaine}
Durée estimée : {mission.duree_estimee_jours or "Non précisée"} jours

CONTACTS
--------
Client : {client.get_full_name()} ({client.email})
Consultant : {consultant.get_full_name()} ({consultant.email})

PROCHAINES ÉTAPES
-----------------
Vous pouvez désormais échanger directement afin de finaliser
les modalités de la mission.

AMEE reste disponible pour tout accompagnement.

Cordialement,
Equipe AMEE
"""

    send_mail(
        subject=f"Mise en relation confirmée – {mission.titre}",
        message=message,
        from_email="noreply@amee.org",
        recipient_list=[client.email, consultant.email],
    )


@receiver(post_save, sender=ContactRequest)
def demander_feedback(sender, instance, **kwargs):

    if instance.statut != "MISSION_TERMINEE":
        return

    if hasattr(instance, "feedback"):
        return

    send_mail(
        subject="Merci d'évaluer votre mission",
        message=f"Lien feedback : /feedback/{instance.id}/",
        recipient_list=[instance.client.email],
        from_email="noreply@amee.org"
    )