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

from django.db.models import Sum
from django.utils import timezone

from accounts.models import User
from tresorerie.models import Transaction
from roster.models import ConsultantProfile
from missions.models import Mission


@login_required
def dashboard(request):

    # -----------------------
    # MEMBRES
    # -----------------------
    membres_actifs = User.objects.filter(
        adhesion__date_expiration__gte=timezone.now().date()
    ).count()

    consultants = User.objects.filter(
        role="CONSULTANT"
    ).count()

    # -----------------------
    # ROSTER
    # -----------------------
    roster_attente = ConsultantProfile.objects.filter(
        statut="EN_ATTENTE"
    ).count()

    # -----------------------
    # MISSIONS
    # -----------------------
    missions_ouvertes = Mission.objects.filter(
        statut="OUVERTE"
    ).count()

    # -----------------------
    # TRESORERIE
    # -----------------------
    entrees = Transaction.objects.filter(
        type_transaction="ENTREE",
        statut="VALIDEE"
    ).aggregate(total=Sum("montant"))["total"] or 0

    sorties = Transaction.objects.filter(
        type_transaction="SORTIE",
        statut="VALIDEE"
    ).aggregate(total=Sum("montant"))["total"] or 0

    solde = entrees - sorties

    mois = timezone.now().month

    paiements_mois = Transaction.objects.filter(
        type_transaction="ENTREE",
        statut="VALIDEE",
        date_transaction__month=mois
    ).count()

    context = {
        "membres_actifs": membres_actifs,
        "consultants": consultants,
        "roster_attente": roster_attente,
        "missions_ouvertes": missions_ouvertes,
        "solde": solde,
        "paiements_mois": paiements_mois,
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

from tresorerie.models import Transaction


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

    contacts = ContactRequest.objects.filter(
        mission=mission
    ).select_related("consultant")

    return render(
        request,
        "backoffice/missions/mission_detail.html",
        {
            "mission": mission,
            "contacts": contacts,
        }
    )

#-----------------------------
#
#-----------------------------

