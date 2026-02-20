from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from interactions.models import ContactRequest


@receiver(post_save, sender=ContactRequest)
def envoyer_email_mise_en_relation(sender, instance, created, **kwargs):

    if instance.statut != "MISSION_CONFIRME":
        return

    client = instance.client
    consultant = instance.consultant

    message = f"""
Mise en relation AMEE confirmée.

Client: {client.email}
Consultant: {consultant.email}

Vous pouvez désormais échanger directement.
"""

    send_mail(
        subject="Mise en relation AMEE",
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