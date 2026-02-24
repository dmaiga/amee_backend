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

from interactions.models import ContactRequest


def consultant_notifications(request):

    if not request.user.is_authenticated:
        return {}

    profil = getattr(request.user, "profil_roster", None)

    # uniquement consultant validé
    if not profil or profil.statut != "VALIDE":
        return {}

    sollicitations = ContactRequest.objects.filter(
        consultant=request.user,
        statut="ENVOYE"
    ).count()

    missions_en_cours = ContactRequest.objects.filter(
        consultant=request.user,
        statut="MISSION_CONFIRME"
    ).count()

    return {
        "notif_consultant_solicitations": sollicitations,
        "notif_consultant_missions": missions_en_cours,
    }

def portal_state(request):

    if not request.user.is_authenticated:
        return {}

    user = request.user

    adhesion = getattr(user, "adhesion", None)
    profil = getattr(user, "profil_roster", None)
    member_profile = getattr(user, "member_profile", None)

    # ---------------- BADGE LOGIC ----------------
    badge_label = "Visiteur"
    badge_color = "badge-ghost"

    if adhesion and adhesion.est_actif:
        badge_label = "Membre AMEE"
        badge_color = "badge-primary"

    if profil:
        if profil.statut == "SOUMIS":
            badge_label = "Candidature en cours"
            badge_color = "badge-warning"

        elif profil.statut == "REFUSE":
            badge_label = "Action requise"
            badge_color = "badge-error"

        elif profil.statut == "VALIDE":
            badge_label = "Consultant AMEE"
            badge_color = "badge-success"

    return {
        "profil_roster": profil,
        "est_membre_actif": adhesion.est_actif if adhesion else False,
        "est_consultant_valide": profil and profil.statut == "VALIDE",

        # ⭐ nouveaux éléments
        "portal_badge_label": badge_label,
        "portal_badge_color": badge_color,
        "member_profile": member_profile,
    }


from cms.models import Resource, Article, Opportunity
from django.utils import timezone
from datetime import timedelta


def cms_notifications(request):

    if not request.user.is_authenticated:
        return {}

    # fenêtre "nouveau contenu"
    since = timezone.now() - timedelta(days=7)

    new_resources = Resource.objects.filter(
        cree_le__gte=since
    ).count()

    new_events = Article.objects.filter(
        type__in=["EVENEMENT", "FORMATION"],
        publie=True,
        date_publication__gte=since,
    ).count()

    new_opportunities = Opportunity.objects.filter(
        publie=True,
        cree_le__gte=since,
    ).count()

    total_notifications = (
        new_resources +
        new_events +
        new_opportunities
    )

    return {
        "cms_new_resources": new_resources,
        "cms_new_events": new_events,
        "cms_new_opportunities": new_opportunities,
        "cms_notifications_total": total_notifications,
    }