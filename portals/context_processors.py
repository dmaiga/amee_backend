from interactions.models import ContactRequest

from cms.models import Resource, Article, Opportunity
from django.utils import timezone
from datetime import timedelta

from portals.models import Notification

from interactions.models import ContactRequest
from django.utils import timezone
from datetime import timedelta
from missions.models import MissionApplication

def portal_state(request):

    if not request.user.is_authenticated:
        return {}

    user = request.user

    adhesion = getattr(user, "membership", None)
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


def client_notifications(request):

    if not request.user.is_authenticated:
        return {}

    if not hasattr(request.user, "client_profile"):
        return {}

    since = timezone.now() - timedelta(hours=24)

    # candidatures sur missions publiques
    postulations = MissionApplication.objects.filter(
        mission__client=request.user,
        cree_le__gte=since
    ).count()

    # consultant qui accepte collaboration
    collaborations_confirmees = ContactRequest.objects.filter(
        mission__client=request.user,
        statut="MISSION_CONFIRME",
        cree_le__gte=since
    ).count()

    # feedback à faire (collaboration terminée)
    feedbacks_a_faire = ContactRequest.objects.filter(
        mission__client=request.user,
        statut="MISSION_TERMINEE",
        feedback__isnull=True
    ).count()

    return {
        "notif_postulations": postulations,
        "notif_collaborations": collaborations_confirmees,
        "notif_feedbacks": feedbacks_a_faire,
    }



def consultant_notifications(request):

    if not request.user.is_authenticated:
        return {}

    profil = getattr(request.user, "profil_roster", None)

    if not profil or profil.statut != "VALIDE":
        return {}

    since = timezone.now() - timedelta(hours=24)

    # invitations reçues
    invitations = ContactRequest.objects.filter(
        consultant=request.user,
        statut="ENVOYE",
        cree_le__gte=since
    ).count()

    # missions confirmées récemment
    missions_confirmees = ContactRequest.objects.filter(
        consultant=request.user,
        statut="MISSION_CONFIRME",
        cree_le__gte=since
    ).count()

    # feedback attendu
    feedbacks = ContactRequest.objects.filter(
        consultant=request.user,
        statut="MISSION_TERMINEE",
        feedback__isnull=True
    ).count()

    return {
        "notif_consultant_invitations": invitations,
        "notif_consultant_missions": missions_confirmees,
        "notif_consultant_feedbacks": feedbacks,
    }



def cms_notifications(request):

    if not request.user.is_authenticated:
        return {}

    # fenêtre "nouveau contenu"
    since = timezone.now() - timedelta(hours=24)

    new_resources = Resource.objects.filter(
        cree_le__gte=since
    ).count()

    new_events = Article.objects.filter(
        type__in=["EVENEMENT", "FORMATION","COMMUNIQUE"],
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



def notifications(request):

    if request.user.is_authenticated:

        qs = Notification.objects.filter(
            user=request.user
        )

        unread = qs.filter(is_read=False).count()

        notifications = qs.order_by("-created_at")[:5]

        return {
            "notifications": notifications,
            "unread_notifications": unread
        }

    return {}


from portals.models import ClientProfile
from memberships.models import Membership
from roster.models import ConsultantProfile
from quality_control.models import IncidentReview

def backoffice_counts(request):

    if not request.user.is_authenticated:
        return {}

    return {

        # Entreprises en attente validation
        "bo_new_clients": ClientProfile.objects.filter(
            statut_onboarding="EN_ATTENTE"
        ).count(),

        # Nouveaux membres à vérifier
        "bo_new_members": Membership.objects.filter(
           statut='EN_ATTENTE'
        ).count(),

        # Dossiers experts soumis
        "bo_new_roster": ConsultantProfile.objects.filter(
            statut="SOUMIS"
        ).count(),

        # Incidents ouverts
        "bo_open_incidents": IncidentReview.objects.filter(
            statut="OUVERT"
        ).count(),
    }