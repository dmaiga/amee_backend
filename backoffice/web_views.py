from urllib import request

from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

from backoffice.api.tresorerie.services import TresorerieService
from backoffice.permissions.roster import can_manage_roster

from accounts.models import User
from roster.models import ConsultantProfile
from missions.models import Mission
from interactions.models import ContactRequest

from django.db.models import Prefetch,Sum,Count, Q
from quality_control.models import Feedback,IncidentReview

from django.utils import timezone

from tresorerie.models import Transaction

from django.core.mail import send_mail
from django.contrib import messages




#-----------------------------
#
#-----------------------------


def backoffice_login(request):

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(
            request,
            email=email,
            password=password
        )

        if user:
            login(request, user)
            return redirect("bo_dashboard")

        return render(
            request,
            "backoffice/login.html",
            {"error": "Identifiants invalides"}
        )

    return render(request, "backoffice/login.html")

@login_required
def dashboard(request):
    now = timezone.now()
    trente_jours_ago = now - timezone.timedelta(days=30)

    # --- 👥 Membres & Roster ---
    membres_actifs = User.objects.filter(adhesion__date_expiration__gte=now.date()).count()
    consultants = ConsultantProfile.objects.filter(statut="VALIDE").count()
    roster_attente = ConsultantProfile.objects.filter(statut="EN_ATTENTE").count()
    
    # Nouveau : Taux de conversion (Membres -> Consultants)
    taux_conversion = 0
    if membres_actifs > 0:
        taux_conversion = round((consultants / membres_actifs) * 100, 1)

    # --- 💰 Trésorerie ---
    solde = TresorerieService.get_solde()
    # Entrées du mois dernier pour voir la tendance
    entrees_mois = Transaction.objects.filter(
        type_transaction="ENTREE", 
        statut="VALIDEE",
        date_transaction__gte=trente_jours_ago
    ).aggregate(Sum('montant'))['montant__sum'] or 0

    # --- 🤝 Missions & Qualité ---
    missions_ouvertes = Mission.objects.filter(statut="OUVERTE").count()
    total_contacts = ContactRequest.objects.count()
    
    # Nouveau : Alertes Incidents non résolus
    incidents_critiques = IncidentReview.objects.filter(statut="A_TRAITER").count()

    context = {
        "membres_actifs": membres_actifs,
        "consultants": consultants,
        "roster_attente": roster_attente,
        "taux_conversion": taux_conversion,
        "missions_ouvertes": missions_ouvertes,
        "total_contacts": total_contacts,
        "solde": solde,
        "entrees_mois": entrees_mois,
        "incidents_critiques": incidents_critiques,
    }
    return render(request, "backoffice/dashboard.html", context)

#-----------------------------
#
#-----------------------------

@login_required
def tresorerie_paiement(request):

    context = {}

    if request.method == "POST":

        operation = request.POST.get("operation")

        base_data = {
            "type_transaction": "ENTREE",
            "montant": int(request.POST.get("montant")),
            "email_payeur": request.POST.get("email_payeur"),
            "description": request.POST.get("description"),
        }

        transactions = []

        # -----------------------------
        # ADHESION COMPLETE
        # -----------------------------
        if operation == "FULL":

            t1 = TresorerieService.enregistrer_paiement(
                user=request.user,
                data={**base_data, "categorie": "ADHESION"}
            )

            t2 = TresorerieService.enregistrer_paiement(
                user=request.user,
                data={**base_data, "categorie": "COTISATION"}
            )

            transactions = [t1, t2]

        elif operation == "COTISATION":

            t = TresorerieService.enregistrer_paiement(
                user=request.user,
                data={**base_data, "categorie": "COTISATION"}
            )
            transactions = [t]

        elif operation == "ADHESION":

            t = TresorerieService.enregistrer_paiement(
                user=request.user,
                data={**base_data, "categorie": "ADHESION"}
            )
            transactions = [t]

        # -----------------------------
        # RÉCUPÉRATION ÉTAT MEMBRE
        # -----------------------------
        last_transaction = transactions[-1]
        user = last_transaction.membre

        membership = getattr(user, "adhesion", None)

        context["result"] = {
            "transactions": transactions,
            "user": user,
            "membership": membership,
            "cree_par": request.user,
        }

    return render(
        request,
        "backoffice/tresorerie/tresorerie_form.html",
        context
    )

@login_required
def tresorerie_depense(request):

    context = {}

    if request.method == "POST":

        data = {
            "type_transaction": "SORTIE",
            "categorie": request.POST.get("categorie"),
            "montant": int(request.POST.get("montant")),
            "description": request.POST.get("description"),
        }

        transaction = TresorerieService.enregistrer_paiement(
            user=request.user,
            data=data
        )

        context["success"] = f"Dépense #{transaction.id} enregistrée ✅"

    return render(
        request,
        "backoffice/tresorerie/depense_form.html",
        context
    )



@login_required
def transactions_list(request):

    type_transaction = request.GET.get("type")

    transactions = Transaction.objects.select_related(
        "membre",
        "cree_par"
    ).order_by("-cree_le")
    from django.db.models import Sum, Q

    entrees = Transaction.objects.filter(
        type_transaction="ENTREE",
        statut="VALIDEE"
    ).aggregate(total=Sum("montant"))["total"] or 0

    sorties = Transaction.objects.filter(
        type_transaction="SORTIE",
        statut="VALIDEE"
    ).aggregate(total=Sum("montant"))["total"] or 0

    solde = entrees - sorties

    if type_transaction:
        transactions = transactions.filter(
            type_transaction=type_transaction
        )

    context = {
        "transactions": transactions,
        "selected_type": type_transaction,
        "solde": solde,
        "entrees": entrees,
        "sorties": sorties,
    }

    return render(
        request,
        "backoffice/tresorerie/transactions_list.html",
        context
    )

@login_required
def transaction_detail(request, transaction_id):

    transaction = get_object_or_404(
        Transaction.objects.select_related(
            "membre",
            "cree_par"
        ),
        pk=transaction_id
    )

    return render(
        request,
        "backoffice/tresorerie/transaction_detail.html",
        {"transaction": transaction}
    )


#-----------------------------
#
#-----------------------------
@login_required
def membres_list(request):

    role = request.GET.get("role")

    # ----------------------
    # RESEAU AMEE
    # ----------------------
    membres = User.objects.filter(
        id_membre_association__isnull=False
    ).select_related("adhesion").exclude(role="SUPERADMIN")

    if role:
        membres = membres.filter(role=role)

    membres = membres.order_by("-id")

    # ----------------------
    # CLIENTS EXTERNES
    # ----------------------
    clients = User.objects.filter(
        role="CLIENT"
    ).order_by("-id")

    context = {
        "membres": membres,
        "clients": clients,
        "selected_role": role,
        "roles": User.ROLE_CHOICES,
    }

    return render(
        request,
        "backoffice/membres/membres_list.html",
        context
    )


@login_required
def membre_detail(request, user_id):

    user = get_object_or_404(
        User.objects.select_related("adhesion"),
        pk=user_id
    )

    derniere_transaction = (
        user.transactions
        .filter(statut="VALIDEE")
        .order_by("-date_transaction")
        .first()
    )

    try:
        roster_profile = user.profil_roster
    except ConsultantProfile.DoesNotExist:
        roster_profile = None

    context = {
        "membre": user,
        "membership": getattr(user, "adhesion", None),
        "derniere_transaction": derniere_transaction,
        "roster_profile": roster_profile,
    }

    return render(
        request,
        "backoffice/membres/membre_detail.html",
        context
    )

#-----------------------------
#
#-----------------------------


@login_required
def roster_list(request):

    statut = request.GET.get("statut")

    profils = ConsultantProfile.objects.select_related(
        "user",
        "user__adhesion"
    )

    if statut:
        profils = profils.filter(statut=statut)

    context = {
        "profils": profils.order_by("-id"),
        "selected_statut": statut,
        "statuts": ConsultantProfile._meta.get_field("statut").choices,
    }

    return render(
        request,
        "backoffice/roster/roster_list.html",
        context
    )

@login_required
def roster_detail(request, profil_id):

    profil = get_object_or_404(
        ConsultantProfile.objects.select_related("user"),
        pk=profil_id
    )

    return render(
        request,
        "backoffice/roster/roster_detail.html",
        {"profil": profil}
    )


@require_POST
@login_required
def roster_decision(request, profil_id):

    if not can_manage_roster(request.user):
        return HttpResponseForbidden("Accès refusé")

    profil = get_object_or_404(ConsultantProfile, pk=profil_id)

    action = request.POST.get("action")

    if action == "valider":
        profil.statut = "VALIDE"
        profil.save(update_fields=["statut"])

        user = profil.user
        user.role = "CONSULTANT"
        user.save(update_fields=["role"])

    elif action == "refuser":
        profil.statut = "REFUSE"
        profil.save(update_fields=["statut"])

    return redirect("bo_roster_detail", profil_id=profil.id)

#-----------------------------
#
#-----------------------------

@login_required
def missions_list(request):


    missions = (
        Mission.objects
        .select_related("client")
        .annotate(
            incidents=Count(
                "contacts__feedback",
                filter=Q(contacts__feedback__incident_signale=True)
            )
        )
        .order_by("-id")
    )

    return render(
        request,
        "backoffice/missions/missions_list.html",
        {"missions": missions}
    )



@login_required
def mission_detail(request, mission_id):

    mission = get_object_or_404(
        Mission.objects.select_related("client"),
        pk=mission_id
    )

    contacts = (
        ContactRequest.objects
        .filter(mission=mission)
        .select_related(
            "consultant",
            "feedback",
            "feedback__incident"   
        )
    )

    return render(
        request,
        "backoffice/missions/mission_detail.html",
        {
            "mission": mission,
            "contacts": contacts,
        }
    )



@login_required
def demander_feedback(request, contact_id):

    contact = get_object_or_404(ContactRequest, pk=contact_id)

    if contact.statut != "MISSION_TERMINEE":
        messages.error(request, "La mission n'est pas terminée.")
        return redirect("bo_mission_detail", mission_id=contact.mission.id)

    if hasattr(contact, "feedback"):
        messages.warning(request, "Feedback déjà reçu.")
        return redirect("bo_mission_detail", mission_id=contact.mission.id)
    
    # 🔴 empêche double relance
    if contact.suivi_envoye:
        messages.info(request, "Une demande de feedback a déjà été envoyée.")
        return redirect("bo_mission_detail", mission_id=contact.mission.id)

    # envoi email
    lien = f"/feedback/{contact.id}/"

    send_mail(
        subject="Merci d'évaluer votre mission AMEE",
        message=f"""
Bonjour,

Votre mission est terminée.
Merci de partager votre retour :

{lien}

AMEE – Qualité réseau
""",
        from_email="noreply@amee.org",
        recipient_list=[contact.client.email],
    )

    contact.suivi_envoye = True
    contact.save(update_fields=["suivi_envoye"])

    messages.success(request, "Demande de feedback envoyée.")

    return redirect("bo_mission_detail", mission_id=contact.mission.id)
#-----------------------------
#
#-----------------------------

@login_required
def incidents_list(request):

    incidents = (
        IncidentReview.objects
        .select_related(
            "consultant",
            "contact_request__mission",
            "feedback",
        )
        .order_by("-cree_le")
    )

    return render(
        request,
        "backoffice/qualites/incidents_list.html",
        {"incidents": incidents}
    )

@login_required
def feedback_detail(request, feedback_id):

    feedback = get_object_or_404(
        Feedback.objects.select_related(
            "contact_request__mission",
            "contact_request__consultant",
            "client"
        ),
        pk=feedback_id
    )

    return render(
        request,
        "backoffice/qualites/feedback_detail.html",
        {"feedback": feedback}
    )