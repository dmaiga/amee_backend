from interactions.models import ContactRequest

def client_notifications(request):

    if not request.user.is_authenticated:
        return {}

    if not hasattr(request.user, "client_profile"):
        return {}

    feedbacks_a_faire = ContactRequest.objects.filter(
        mission__client=request.user,
        statut="MISSION_TERMINEE",
        feedback__isnull=True
    ).count()

    demandes_en_attente = ContactRequest.objects.filter(
        mission__client=request.user,
        statut="ENVOYE"
    ).count()

    return {
        "notif_feedbacks": feedbacks_a_faire,
        "notif_attente": demandes_en_attente,
    }