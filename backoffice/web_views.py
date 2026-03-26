#backoffice/web_views.py
from urllib import request
from django import forms
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse   
from django.db.models import Prefetch,Sum,Count, Q,Max,Avg
from django.db.models import Case, When, Value, IntegerField
from django.utils import timezone

from django.utils import timezone
from django.core.mail import send_mail
from django.contrib import messages




from backoffice.api.tresorerie.services import TresorerieService
from backoffice.permissions.roster import can_manage_roster

from accounts.models import User
from roster.models import ConsultantProfile
from missions.models import Mission,MissionApplication
from interactions.models import ContactRequest
from cms.models import Article, Resource, Opportunity

from quality_control.models import Feedback,IncidentReview


from tresorerie.models import Transaction

from backoffice.forms import (
    ArticleForm,ResourceForm,
    OpportunityForm,AffecterIncidentForm,
    StatuerIncidentForm, EnrolementOrganisationForm,
    PaiementCreationOrganisationForm,CotisationOrganisationForm
    )
from portals.models import Notification
from django.urls import reverse


from memberships.models import Membership
    
from organizations.models import Organization
from memberships.models import Membership

from organizations.models import Organization

from backoffice.forms import OrganizationForm

from datetime import timedelta
from django.utils import timezone

from backoffice.service_paiement import PaiementService
from tresorerie.services import TresorerieService
from tresorerie.forms import TransactionAjustementForm

from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from portals.models import ClientProfile
import secrets
import string

import uuid

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction

from django.contrib.auth import get_user_model

from tresorerie.forms import EnrolementPaiementForm,PaiementSimpleForm,ActivationDigitaleForm

User = get_user_model()

#-----------------------------
#
#-----------------------------
from django.shortcuts import redirect
from django.contrib import messages

def bureau_required(view_func):
    def wrapper(request, *args, **kwargs):

        if not request.user.est_membre_bureau_actif:
            messages.error(request, "Accès réservé au bureau exécutif.")
            return redirect("portal_dashboard")

        return view_func(request, *args, **kwargs)

    return wrapper

#@bureau_required 
@login_required
def dashboard(request):
    now = timezone.now()
    trente_jours_ago = now - timezone.timedelta(days=30)

    # --- 👥 Membres & Roster ---
    membres_actifs = User.objects.filter(adhesions_validation__date_expiration__gte=now.date()).count()
    consultants = ConsultantProfile.objects.filter(statut="VALIDE").count()
    roster_attente = ConsultantProfile.objects.filter(statut="SOUMIS").count()
    
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
    incidents_critiques = IncidentReview.objects.filter(statut="OUVERT").count()

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
def enrolement_dashboard(request):

    today = timezone.now().date()
    limite = today - timedelta(days=365)

    # =====================================================
    # INDIVIDUS
    # =====================================================

    individus = (
        User.objects
        .filter(id_membre_association__isnull=False)
        .annotate(
            derniere_cotisation=Max(
                "transactions__date_transaction",
                filter=Q(
                    transactions__categorie="COTISATION",
                    transactions__statut="VALIDEE"
                )
            )
        )
    )

    individus_a_jour = individus.filter(
        derniere_cotisation__gte=limite
    )

    individus_relance = individus.filter(
        Q(derniere_cotisation__lt=limite) |
        Q(derniere_cotisation__isnull=True)
    )

    # =====================================================
    # BUREAUX
    # =====================================================

    bureaux = (
        Organization.objects
        .annotate(
            derniere_cotisation=Max(
                "transactions__date_transaction",
                filter=Q(
                    transactions__categorie="COTISATION_ORG",
                    transactions__statut="VALIDEE"
                )
            )
        )
    )

    bureaux_a_jour = bureaux.filter(
        derniere_cotisation__gte=limite
    )

    bureaux_relance = bureaux.filter(
        Q(derniere_cotisation__lt=limite) |
        Q(derniere_cotisation__isnull=True) |
        Q(est_actif=False)
    )

    # =====================================================
    context = {
        # KPI
        "individus_a_jour": individus_a_jour.count(),
        "individus_relance": individus_relance.count(),
        "bureaux_a_jour": bureaux_a_jour.count(),
        "bureaux_relance": bureaux_relance.count(),

        # tables
        "liste_individus_relance": individus_relance[:10],
        "liste_bureaux_relance": bureaux_relance[:10],
    }

    return render(
        request,
        "backoffice/tresorerie/dashboard.html",
        context
    )

@login_required
def paiement_bureau(request):

    if request.method == "POST":
        form = CotisationOrganisationForm(request.POST)

        if form.is_valid():

            TresorerieService.cotisation_organisation(
                user=request.user,
                organization=form.cleaned_data["organization"],
                montant=form.cleaned_data["montant"],
                description=form.cleaned_data["description"],
            )

            messages.success(request, "Cotisation enregistrée.")
            return redirect("bo_enrolement_dashboard")

    else:
        form = CotisationOrganisationForm()

    return render(
        request,
        "backoffice/tresorerie/cotisation_organisation.html",
        {"form": form},
    )


@login_required
def enroulement_paiement(request):

    if request.method == "GET":
        token = str(uuid.uuid4())
        request.session["paiement_token"] = token

        return render(
            request,
            "backoffice/tresorerie/enroulemnt_form.html",
            {
                "form": EnrolementPaiementForm(),
                "paiement_token": token,
            },
        )

    form = EnrolementPaiementForm(request.POST, request.FILES)

    if not form.is_valid():
        return render(
            request,
            "backoffice/tresorerie/enroulemnt_form.html",
            {"form": form}
        )

    if request.POST.get("paiement_token") != request.session.get("paiement_token"):
        messages.warning(request, "Paiement déjà traité.")
        return redirect("bo_enrolement_dashboard")

    # empêcher double paiement
    del request.session["paiement_token"]

    data = form.cleaned_data

    # =============================
    # USER
    # =============================
    membre, _ = User.objects.update_or_create(
        email=data["email"],
        defaults={
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "phone": data["phone"],
            "organization": data["organization"],
            "role": "MEMBER",
        }
    )

    # =============================
    # MEMBERSHIP
    # =============================
    Membership.objects.update_or_create(
        user=membre,
        defaults={
            "eligibilite_option": data["eligibilite_option"],
            "diplome_niveau": data.get("diplome_niveau"),
            "diplome_intitule": data.get("diplome_intitule"),
            "annee_diplome": data.get("annee_diplome"),
            "cv_document": request.FILES.get("cv_document"),
            "diplome_document": request.FILES.get("diplome_document"),
        }
    )

    # =============================
    # PAIEMENT
    # =============================
    from django.db import transaction as db_transaction
    
    with db_transaction.atomic():
    
        operation = data["operation"]
    
        if operation == "ADHESION":
        
            if not data["montant_adhesion"]:
                form.add_error("montant_adhesion", "Montant requis.")
                return render(request, "backoffice/tresorerie/enroulemnt_form.html", {"form": form})
    
            TresorerieService.enregistrer_paiement(
                user=request.user,
                data={
                    "type_transaction": "ENTREE",
                    "categorie": "ADHESION",
                    "montant": data["montant_adhesion"],
                    "membre": membre,
                    "email_payeur": membre.email,
                    "description": data.get("description", "Adhésion membre"),
                }
            )
    
        elif operation == "COTISATION":
        
            if not data["montant_cotisation"]:
                form.add_error("montant_cotisation", "Montant requis.")
                return render(request, "backoffice/tresorerie/enroulemnt_form.html", {"form": form})
    
            TresorerieService.enregistrer_paiement(
                user=request.user,
                data={
                    "type_transaction": "ENTREE",
                    "categorie": "COTISATION",
                    "montant": data["montant_cotisation"],
                    "membre": membre,
                    "email_payeur": membre.email,
                    "description": data.get("description", "Cotisation annuelle"),
                }
            )
    
        elif operation == "FULL":
        
            if not data["montant_adhesion"] or not data["montant_cotisation"]:
                form.add_error(None, "Montants requis pour adhésion complète.")
                return render(request, "backoffice/tresorerie/enroulemnt_form.html", {"form": form})
    
            # 1️⃣ Adhésion
            TresorerieService.enregistrer_paiement(
                user=request.user,
                data={
                    "type_transaction": "ENTREE",
                    "categorie": "ADHESION",
                    "montant": data["montant_adhesion"],
                    "membre": membre,
                    "email_payeur": membre.email,
                    "description": "Adhésion membre",
                }
            )
    
            # 2️⃣ Cotisation
            TresorerieService.enregistrer_paiement(
                user=request.user,
                data={
                    "type_transaction": "ENTREE",
                    "categorie": "COTISATION",
                    "montant": data["montant_cotisation"],
                    "membre": membre,
                    "email_payeur": membre.email,
                    "description": "Cotisation annuelle",
                }
            )

    messages.success(request, "Enrôlement enregistré.")
    return redirect("bo_enrolement_dashboard")

@login_required
def tresorerie_paiement_simple(request):

    if request.method == "POST":
        form = PaiementSimpleForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            user = User.objects.filter(email=data["email"]).first()

            if not user:
                messages.error(request, "Membre introuvable.")
                return redirect("bo_paiement_simple")

            # 🔥 Forcer COTISATION
            TresorerieService.enregistrer_paiement(
                user=request.user,
                data={
                    "type_transaction": "ENTREE",
                    "categorie": "COTISATION",
                    "montant": data["montant"],
                    "membre": user,
                    "email_payeur": user.email,
                    "description": data["description"],
                }
            )

            messages.success(request, "Cotisation enregistrée.")
            return redirect("bo_enrolement_dashboard")

    else:
        form = PaiementSimpleForm()

    return render(request,
                  "backoffice/tresorerie/paiement_simple.html",
                  {"form": form})


@login_required
def tresorerie_activation(request, user_id):

    user = get_object_or_404(
        User.objects.select_related("membership"),
        pk=user_id
    )

    membership = user.membership

    if request.method == "POST":
        form = ActivationDigitaleForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            # 1️⃣ ADHESION
            TresorerieService.enregistrer_paiement(
                user=request.user,
                data={
                    "type_transaction": "ENTREE",
                    "categorie": "ADHESION",
                    "montant": data["montant_adhesion"],
                    "membre": user,
                    "email_payeur": user.email,
                    "description": "Adhésion digitale",
                }
            )

            # 2️⃣ COTISATION
            TresorerieService.enregistrer_paiement(
                user=request.user,
                data={
                    "type_transaction": "ENTREE",
                    "categorie": "COTISATION",
                    "montant": data["montant_cotisation"],
                    "membre": user,
                    "email_payeur": user.email,
                    "description": "Cotisation annuelle",
                }
            )

            messages.success(request, "Activation effectuée.")
            return redirect("bo_enrolement_dashboard")

    else:
        form = ActivationDigitaleForm()

    return render(
        request,
        "backoffice/tresorerie/activation.html",
        {"form": form, "membre": user}
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
        return redirect("bo_transactions")
    return render(
        request,
        "backoffice/tresorerie/depense_form.html",
        context
    )


from django.core.paginator import Paginator
from django.utils.dateparse import parse_date
from datetime import datetime

@login_required
def transactions_list(request):

    type_transaction = request.GET.get("type")
    date_debut = request.GET.get("date_debut")
    date_fin = request.GET.get("date_fin")

    transactions = Transaction.objects.select_related(
        "membre",
        "cree_par"
    ).order_by("-cree_le")

    from django.db.models import Sum

    # -------------------------
    # FILTRES
    # -------------------------
    if type_transaction:
        transactions = transactions.filter(type_transaction=type_transaction)

    if date_debut:
        transactions = transactions.filter(date_transaction__gte=parse_date(date_debut))

    if date_fin:
        transactions = transactions.filter(date_transaction__lte=parse_date(date_fin))

    # -------------------------
    # STATS (filtrées aussi 👈)
    # -------------------------
    base_qs = transactions.filter(statut="VALIDEE")

    entrees = base_qs.filter(type_transaction="ENTREE").aggregate(
        total=Sum("montant")
    )["total"] or 0

    sorties = base_qs.filter(type_transaction="SORTIE").aggregate(
        total=Sum("montant")
    )["total"] or 0

    solde = entrees - sorties

    # -------------------------
    # PAGINATION
    # -------------------------
    paginator = Paginator(transactions, 10)  # 10 par page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "transactions": page_obj,
        "page_obj": page_obj,
        "selected_type": type_transaction,
        "date_debut": date_debut,
        "date_fin": date_fin,
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

@login_required
def transaction_ajuster(request, transaction_id):

    transaction = get_object_or_404(Transaction, pk=transaction_id)

    if transaction.statut != "VALIDEE":
        messages.error(request, "Seules les transactions validées peuvent être ajustées.")
        return redirect("transaction_detail", transaction_id=transaction.id)

    form = TransactionAjustementForm(request.POST or None)

    if form.is_valid():
        ajustement = form.save(commit=False)

        ajustement.categorie = transaction.categorie
        ajustement.membre = transaction.membre
        ajustement.organization = transaction.organization

        ajustement.transaction_reference = transaction
        ajustement.est_ajustement = True
        ajustement.statut = "VALIDEE"
        ajustement.cree_par = request.user

        ajustement.save()

        # ⚠️ Important : appliquer logique métier si ENTREE
        from tresorerie.services import appliquer_transaction
        appliquer_transaction(ajustement)

        messages.success(request, "Ajustement appliqué.")
        return redirect("bo_transaction_detail", transaction_id=transaction.id)

    return render(
        request,
        "backoffice/tresorerie/transaction_ajustement_form.html",
        {
            "form": form,
            "transaction": transaction
        }
    )
#-----------------------------
#
#-----------------------------

@login_required
def membres_list(request):

    statut = request.GET.get("statut")

    dossiers = (
        Membership.objects
        .select_related("user", "user__organization")
        .exclude(user__role="SUPERADMIN")
        .order_by("-cree_le")
    )

    if statut:
        dossiers = dossiers.filter(statut=statut)

    context = {
        "dossiers": dossiers,
        "selected_statut": statut,
        "statuts": Membership.STATUT,
    }

    return render(
        request,
        "backoffice/membres/membres_list.html",
        context
    )

@login_required
def membre_detail(request, user_id):

    user = get_object_or_404(
        User.objects.select_related(
            "membership",
            "profil_roster"
        ),
        pk=user_id
    )

    membership = getattr(user, "membership", None)

    derniere_transaction = (
        user.transactions
        .filter(statut="VALIDEE")
        .order_by("-date_transaction")
        .first()
    )

    # ===============================
    # ACTIONS DOSSIER
    # ===============================
    if request.method == "POST" and membership:

        action = request.POST.get("action")

        # ❌ REFUSER
        if action == "refuser":

            membership.statut = "REFUSE"
            membership.valide_par = request.user
            membership.motif_refus = request.POST.get("motif")
            membership.save()

            messages.success(request, "Candidature refusée.")
            return redirect("bo_membre_detail", user_id=user.id)

        # ✅ ACCEPTER → direction trésorerie
        elif action == "accepter":
            return redirect("bo_activation", user_id=user.id)

    context = {
        "membre": user,
        "membership": membership,
        "derniere_transaction": derniere_transaction,
        "roster_profile": getattr(user, "profil_roster", None),
    }

    return render(
        request,
        "backoffice/membres/membre_detail.html",
        context
    )

@login_required
def clients_list(request):

    statut = request.GET.get("statut")

    clients = ClientProfile.objects.select_related("user")

    if statut == "en_attente":
        clients = clients.filter(est_verifie=False)

    elif statut == "verifies":
        clients = clients.filter(est_verifie=True)

    clients = clients.order_by("-cree_le")

    return render(
        request,
        "backoffice/clients/clients_list.html",
        {
            "clients": clients,
            "selected_statut": statut,
        }
    )


@login_required
def client_detail(request, pk):

    client = get_object_or_404(
        ClientProfile.objects.select_related("user"),
        pk=pk
    )

    user = client.user
    contacts = user.demandes_clients

    # -------------------------
    # MISSIONS
    # -------------------------
    missions_stats = user.missions.aggregate(
        total=Count("id"),
        actives=Count("id", filter=Q(statut="ACTIVE")),
        terminees=Count("id", filter=Q(statut="TERMINEE ")),
    )

    # -------------------------
    # COLLABORATIONS REELLES
    # consultants uniques
    # -------------------------
    collaboration_stats = contacts.filter(
        est_collaboration_validee=True
    ).aggregate(
        consultants_uniques=Count("consultant", distinct=True),
        collaborations=Count("id"),
        missions_terminees=Count(
            "id",
            filter=Q(statut="MISSION_TERMINEE")
        ),
    )

    # -------------------------
    # FEEDBACK DONNE PAR LE CLIENT
    # -------------------------
    feedback_stats = contacts.filter(
        feedback__isnull=False
    ).aggregate(
        total_feedback=Count("feedback"),
        note_moyenne=Avg("feedback__note"),
        incidents=Count(
            "feedback",
            filter=Q(feedback__incident_signale=True)
        ),
    )

    # -------------------------
    # STATUT CLIENT SIMPLE
    # -------------------------
    if collaboration_stats["consultants_uniques"] == 0:
        statut_client = "INACTIF"
    elif collaboration_stats["consultants_uniques"] < 3:
        statut_client = "EN_DEMARRAGE"
    else:
        statut_client = "ACTIF"

    return render(
        request,
        "backoffice/clients/client_detail.html",
        {
            "client": client,
            "missions_stats": missions_stats,
            "collaboration_stats": collaboration_stats,
            "feedback_stats": feedback_stats,
            "statut_client": statut_client,
        }
    )


@login_required
def valider_client(request, pk):

    client = get_object_or_404(ClientProfile, pk=pk)

    if client.est_verifie:
        messages.info(request, "Client déjà validé.")
        return redirect("client_detail", pk=pk)

    # -----------------------------
    # Génération nouveau password
    # -----------------------------
    password = secrets.token_urlsafe(10)

    user = client.user
    user.set_password(password)
    user.is_active = True
    user.save()

    # -----------------------------
    # Validation profil
    # -----------------------------
    client.est_verifie = True
    client.statut_onboarding = "VALIDE"
    client.valide_par = request.user
    client.save()

    # -----------------------------
    # EMAIL ACCÈS
    # -----------------------------
    send_mail(
        subject="Activation de votre espace client AMEE",
        message=(
            f"Bonjour {client.nom_contact},\n\n"
            f"Votre entreprise a été validée par notre équipe.\n\n"
            f"Vos accès :\n"
            f"Identifiant : {client.email_pro}\n"
            f"Mot de passe : {password}\n\n"
            f"Connexion : https://amee.org/login/\n\n"
            f"Nous vous conseillons de modifier votre mot de passe après connexion.\n\n"
            f"L’équipe AMEE"
        ),
        from_email=None,
        recipient_list=[client.email_pro],
        fail_silently=True,
    )

    messages.success(request, "Client validé et accès envoyés.")

    return redirect("client_detail", pk=pk)

@login_required
def refuser_client(request, pk):

    client = get_object_or_404(ClientProfile, pk=pk)

    client.user.is_active = False
    client.user.save()

    messages.warning(request, "Client refusé.")

    return redirect("clients_list")

#-----------------------------
#
#-----------------------------



@login_required
def roster_list(request):

    statut = request.GET.get("statut")

    profils = (
        ConsultantProfile.objects
        .select_related(
            "user",
            "user__membership",
            "user__organization",
        )
    )

    if statut:
        profils = profils.filter(statut=statut)

    # 🔥 priorité visuelle :
    # SOUMIS → VALIDE → REFUSE
    profils = profils.annotate(
        ordre_statut=Case(
            When(statut="SOUMIS", then=Value(0)),
            When(statut="VALIDE", then=Value(1)),
            default=Value(2),
            output_field=IntegerField(),
        )
    ).order_by("ordre_statut", "-id")

    context = {
        "profils": profils,
        "selected_statut": statut,
        "statuts": ConsultantProfile._meta.get_field("statut").choices,
        "today": timezone.now().date(),
    }

    return render(
        request,
        "backoffice/roster/roster_list.html",
        context
    )

@login_required
def roster_detail(request, profil_id):

    profil = get_object_or_404(
        ConsultantProfile.objects
        .select_related(
            "user",
            "user__membership",
        )
        .prefetch_related("historique"),
        pk=profil_id
    )

    return render(
        request,
        "backoffice/roster/roster_detail.html",
        {
            "profil": profil,
        }
    )


@require_POST
@login_required
def roster_decision(request, profil_id):

    if not can_manage_roster(request.user):
        return HttpResponseForbidden("Accès refusé")

    profil = get_object_or_404(ConsultantProfile, pk=profil_id)

    action = request.POST.get("action")

    if action == "valider":
        profil.valider(validateur=request.user)

    elif action == "refuser":

        motif = request.POST.get("motif_refus")

        if not motif:
            messages.error(request, "Veuillez préciser le motif du refus.")
            return redirect("bo_roster_detail", profil_id=profil.id)

        profil.refuser(
            validateur=request.user,
            motif=motif
        )

    return redirect("bo_roster_detail", profil_id=profil.id)


#-----------------------------
#
#-----------------------------

from django.db.models import Count, Q

from django.db.models import Count, Q

@login_required
def missions_list(request):

    # Missions ciblées (via ContactRequest)
    missions_ciblees = (
        Mission.objects
        .filter(contacts__isnull=False)
        .select_related("client")
        .annotate(
            nb_consultants=Count("contacts", distinct=True)
        )
        .distinct()
        .order_by("-cree_le")
    )

    # Missions publiques avec au moins un RETENU
    missions_publiques = (
        Mission.objects
        .filter(applications__statut="RETENU")
        .select_related("client")
        .annotate(
            nb_consultants=Count(
                "applications",
                filter=Q(applications__statut="RETENU"),
                distinct=True
            )
        )
        .distinct()
        .order_by("-cree_le")
    )

    return render(
        request,
        "backoffice/missions/missions_list.html",
        {
            "missions_ciblees": missions_ciblees,
            "missions_publiques": missions_publiques,
        }
    )

from django.db.models import Count, Q

@login_required
def mission_detail(request, mission_id):

    mission = get_object_or_404(
        Mission.objects.select_related("client"),
        pk=mission_id
    )

    contacts = (
        ContactRequest.objects
        .filter(mission=mission)
        .select_related("consultant", "feedback", "feedback__incident")
    )

    # ✅ Mises en relation réelles (confirmées)
    mises_en_relation = contacts.filter(
        statut__in=["MISSION_CONFIRME", "MISSION_TERMINEE"]
    )

    # ✅ Applications publiques retenues uniquement
    applications_retenues = (
        mission.applications
        .filter(statut="RETENU")
        .select_related("consultant")
    )

    return render(
        request,
        "backoffice/missions/mission_detail.html",
        {
            "mission": mission,
            "contacts": contacts,
            "applications_retenues": applications_retenues,
            "mises_en_relation_count": mises_en_relation.count(),
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
            "enqueteur",
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
            "client",
            "incident", 
        ),
        pk=feedback_id
    )

    return render(
        request,
        "backoffice/qualites/feedback_detail.html",
        {"feedback": feedback}
    )

@login_required
def affecter_incident(request, incident_id):

    incident = get_object_or_404(IncidentReview, pk=incident_id)

    if incident.enqueteur:
        messages.warning(request, "Incident déjà affecté.")
        return redirect(
            "bo_mission_detail",
            mission_id=incident.contact_request.mission.id
        )

    if request.method == "POST":
        form = AffecterIncidentForm(request.POST, instance=incident)

        if form.is_valid():
            incident = form.save(commit=False)
            incident.statut = "ENQUETE"
            incident.save(update_fields=["enqueteur", "statut"])

            messages.success(request, "Incident affecté.")
            return redirect(
                "bo_mission_detail",
                mission_id=incident.contact_request.mission.id
            )
    else:
        form = AffecterIncidentForm(instance=incident)

    return render(
        request,
        "backoffice/qualites/affecter_incident.html",
        {"form": form, "incident": incident},
    )

@login_required
def statuer_incident(request, incident_id):

    incident = get_object_or_404(IncidentReview, pk=incident_id)

    # sécurité enquêteur
    if incident.enqueteur != request.user:
        messages.error(request, "Vous n'êtes pas l'enquêteur assigné.")
        return redirect(
            "bo_mission_detail",
            mission_id=incident.contact_request.mission.id
        )

    if request.method == "POST":
        form = StatuerIncidentForm(request.POST, instance=incident)

        if form.is_valid():
            incident = form.save(commit=False)

            decision = form.cleaned_data["decision"]
            niveau = form.cleaned_data.get("niveau")

            incident.decision = decision
            incident.date_cloture = timezone.now()

            if decision != "NON_LIEU":
                incident.creer_signalement(
                    niveau=niveau,
                    commentaire=incident.rapport_enquete,
                )
            else:
                incident.statut = "CLOTURE"
                incident.save()

            messages.success(request, "Incident clôturé.")
            return redirect(
                "bo_mission_detail",
                mission_id=incident.contact_request.mission.id
            )
    else:
        form = StatuerIncidentForm(instance=incident)

    return render(
        request,
        "backoffice/qualites/enquete_incident.html",
        {
            "incident": incident,
            "form": form,
        },
    )

#-----------------------------
#
#-----------------------------

@login_required
def cms_dashboard(request):

    context = {
        "articles_total": Article.objects.count(),
        "articles_brouillons": Article.objects.filter(publie=False).count(),
        "resources_total": Resource.objects.count(),
        "opportunities_actives":
            Opportunity.objects.filter(publie=True).count(),

        "articles": Article.objects.order_by("-date_publication")[:5],
        "resources": Resource.objects.order_by("-cree_le")[:5],
        "opportunities": Opportunity.objects.order_by("-cree_le")[:5],
    }

    return render(
        request,
        "backoffice/cms/dashboard.html",
        context
    )

# ----------------------------- 

@login_required
def articles_list(request):

    statut = request.GET.get("statut") or ""
    type_article = request.GET.get("type") or ""
    search = request.GET.get("q") or ""

    articles = Article.objects.all().order_by("-date_publication")

    if statut == "publie":
        articles = articles.filter(publie=True)

    elif statut == "brouillon":
        articles = articles.filter(publie=False)

    if type_article:
        articles = articles.filter(type=type_article)

    if search.strip():
        articles = articles.filter(titre__icontains=search.strip())

    return render(
        request,
        "backoffice/cms/articles/articles_list.html",
        {
            "articles": articles,
            "selected_statut": statut,
            "selected_type": type_article,
            "search": search,
            "type_choices": Article.TYPE_CHOICES,  
        }
    )

@login_required
def article_detail(request, article_id):

    article = get_object_or_404(Article, pk=article_id)

    return render(
        request,
        "backoffice/cms/articles/article_detail.html",
        {"article": article}
    )

@login_required
def article_form(request, article_id=None):

    article = None

    if article_id:
        article = get_object_or_404(Article, pk=article_id)

    if request.method == "POST":
        form = ArticleForm(
            request.POST,
            request.FILES,
            instance=article
        )

        if form.is_valid():
            article = form.save(commit=False)
    
            # audit : auteur publication
            if not article.publie_par:
                article.publie_par = request.user
    
            article.save()
            users = User.objects.filter(
                role__in=["MEMBER", "CONSULTANT"]
            )

            for user in users:
                Notification.objects.create(
                    user=user,
                    type="ARTICLES",
                    message=f"Nouveau article publié : {article.titre}",
                    url=reverse("resources_list")
                )


            return redirect("bo_articles_list")

    else:
        form = ArticleForm(instance=article)

    return render(
        request,
        "backoffice/cms/articles/article_form.html",
        {
            "form": form,
            "article": article,
        }
    )

# -----------------------------

@login_required
def ressources_list(request):

    categorie = request.GET.get("categorie") or ""
    acces = request.GET.get("acces") or ""
    search = request.GET.get("q") or ""

    ressources = Resource.objects.all().order_by("-cree_le")

    if categorie:
        ressources = ressources.filter(categorie=categorie)

    if acces == "membres":
        ressources = ressources.filter(reserve_aux_membres=True)

    elif acces == "public":
        ressources = ressources.filter(reserve_aux_membres=False)

    if search.strip():
        ressources = ressources.filter(titre__icontains=search.strip())

    return render(
        request,
        "backoffice/cms/ressources/ressources_list.html",
        {
            "ressources": ressources,
            "categories": Resource.CATEGORIE_CHOICES,
            "selected_categorie": categorie,
            "selected_acces": acces,
            "search": search,
        }
    )

@login_required
def ressource_detail(request, ressource_id):

    ressource = get_object_or_404(Resource, pk=ressource_id)

    return render(
        request,
        "backoffice/cms/ressources/ressource_detail.html",
        {"ressource": ressource}
    )

from portals.models import Notification
from django.urls import reverse
from accounts.models import User

@login_required
def ressource_form(request, ressource_id=None):

    ressource = None

    if ressource_id:
        ressource = get_object_or_404(Resource, pk=ressource_id)

    if request.method == "POST":
        form = ResourceForm(
            request.POST,
            request.FILES,
            instance=ressource
        )

        if form.is_valid():
            ressource = form.save(commit=False)

            if not ressource.publie_par:
                ressource.publie_par = request.user

            ressource.save()

            # 🔔 NOTIFICATION MEMBRES / CONSULTANTS
            users = User.objects.filter(
                role__in=["MEMBER", "CONSULTANT"]
            )

            for user in users:
                Notification.objects.create(
                    user=user,
                    type="RESOURCE",
                    message=f"Nouvelle ressource publiée : {ressource.titre}",
                    url=reverse("resources_list")
                )

            return redirect("bo_ressources_list")

    else:
        form = ResourceForm(instance=ressource)

    return render(
        request,
        "backoffice/cms/ressources/ressource_form.html",
        {
            "form": form,
            "ressource": ressource,
        }
    )
# -----------------------------

@login_required
def opportunities_list(request):

    statut = request.GET.get("statut")

    opportunities = Opportunity.objects.all().order_by("-cree_le")

    if statut == "active":
        opportunities = [o for o in opportunities if not o.est_expire]

    elif statut == "expire":
        opportunities = [o for o in opportunities if o.est_expire]

    return render(
        request,
        "backoffice/cms/opportunities/opportunities_list.html",
        {
            "opportunities": opportunities,
            "selected_statut": statut,
        }
    )

@login_required
def opportunity_detail(request, opportunity_id):

    opportunity = get_object_or_404(Opportunity, pk=opportunity_id)

    return render(
        request,
        "backoffice/cms/opportunities/opportunity_detail.html",
        {"opportunity": opportunity}
    )

@login_required
def opportunity_form(request, opportunity_id=None):

    opportunity = None

    if opportunity_id:
        opportunity = get_object_or_404(Opportunity, pk=opportunity_id)

    if request.method == "POST":
        form = OpportunityForm(
            request.POST,
            request.FILES,
            instance=opportunity
        )

        if form.is_valid():
            opportunity = form.save(commit=False)

            # ✅ QUI A PUBLIÉ
            if not opportunity.publie_par:
                opportunity.publie_par = request.user

            opportunity.save()
            consultants = User.objects.filter(
                role__in=["CONSULTANT", "MEMBER"]
            )

            for user in consultants:
                Notification.objects.create(
                    user=user,
                    type="OPPORTUNITY",
                    message=f"Nouvelle opportunité publiée : {opportunity.titre}",
                    url=reverse("opportunities_list")
                )
            return redirect("bo_opportunities_list")

    else:
        form = OpportunityForm(instance=opportunity)

    return render(
        request,
        "backoffice/cms/opportunities/opportunity_form.html",
        {
            "form": form,
            "opportunity": opportunity,
        }
    )


#-----------------------------
#
#-----------------------------


@login_required
def organisations_list(request):

    filtre = request.GET.get("statut")

    organisations = (
        Organization.objects
        .annotate(
            derniere_cotisation=Max(
                "transactions__date_transaction",
                filter=Q(
                    transactions__categorie="COTISATION_ORG",
                    transactions__statut="VALIDEE"
                )
            )
        )
    )

    today = timezone.now().date()

    # 🔎 filtres simples
    if filtre == "actifs":
        organisations = organisations.filter(
            date_expiration__gte=today
        )

    elif filtre == "expires":
        organisations = organisations.filter(
            date_expiration__lt=today
        )

    elif filtre == "non_affilies":
        organisations = organisations.filter(est_affilie=False)

    organisations = organisations.order_by("nom")

    return render(
        request,
        "backoffice/organisations/organisations_list.html",
        {
            "organisations": organisations,
            "filtre": filtre,
        },
    )

@login_required
def organisation_detail(request, organisation_id):

    organisation = get_object_or_404(
        Organization.objects.prefetch_related("transactions"),
        pk=organisation_id
    )

    transactions = organisation.transactions.order_by("-date_transaction")[:10]

    return render(
        request,
        "backoffice/organisations/organisation_detail.html",
        {
            "organisation": organisation,
            "transactions": transactions,
            "today": timezone.now().date(),
        }
    )


@login_required
def organisation_form(request, organisation_id=None):

    organisation = None

    if organisation_id:
        organisation = get_object_or_404(
            Organization,
            pk=organisation_id
        )

    if request.method == "POST":

        org_form = OrganizationForm(
            request.POST,
            request.FILES,
            instance=organisation
        )

        paiement_form = PaiementCreationOrganisationForm(request.POST)

        if org_form.is_valid() and paiement_form.is_valid():

            organisation = org_form.save()

            op = paiement_form.cleaned_data["operation"]
            adh = paiement_form.cleaned_data["montant_adhesion"]
            cot = paiement_form.cleaned_data.get("montant_cotisation")
            description = paiement_form.cleaned_data.get("description")

            try:

                if op == "FULL":

                    TresorerieService.enroller_organisation(
                        user=request.user,
                        organization=organisation,
                        montant_enrolement=adh,
                        montant_cotisation=cot,
                        description=description,
                    )

                elif op == "ADHESION":

                    TresorerieService.enroller_organisation(
                        user=request.user,
                        organization=organisation,
                        montant_enrolement=adh,
                        description=description,
                    )

                messages.success(
                    request,
                    "Organisation créée et paiement enregistré."
                )

                return redirect("bo_enrolement_dashboard")

            except ValueError as e:
                messages.error(request, str(e))

    else:
        org_form = OrganizationForm(instance=organisation)
        paiement_form = PaiementCreationOrganisationForm()

    return render(
        request,
        "backoffice/organisations/organisation_form.html",
        {
            "form": org_form,
            "paiement_form": paiement_form,
            "organisation": organisation,
        }
    )


from django.shortcuts import render, redirect, get_object_or_404
from cms.models import Mandat, BoardRole, BoardMembership
from cms.forms import MandatForm, BoardRoleForm, BoardMembershipForm


 
def mandat_list(request):
    mandats = Mandat.objects.all().order_by("-date_debut")
    return render(request, "backoffice/cms/governance/mandat_list.html", {"mandats": mandats})

def mandat_create(request):
    form = MandatForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect("mandat_list")

    return render(request, "backoffice/cms/governance/mandat_form.html", {"form": form})

def mandat_detail(request, pk):
    mandat = get_object_or_404(Mandat, pk=pk)

    membres = BoardMembership.objects.filter(
        mandat=mandat
    ).select_related("membership__user", "role")

    return render(request, "backoffice/cms/governance/mandat_detail.html", {
        "mandat": mandat,
        "membres": membres
    })
 
from django.contrib import messages
from django.core.exceptions import ValidationError

def mandat_toggle(request, pk):
    mandat = get_object_or_404(Mandat, pk=pk)

    mandat.actif = not mandat.actif

    try:
        mandat.save()
        messages.success(request, "Statut du mandat mis à jour.")
    except ValidationError as e:
        messages.error(request, e.message_dict.get("__all__", ["Erreur"])[0])

    return redirect("mandat_list")


def boardmembership_add(request, mandat_id):
    mandat = get_object_or_404(Mandat, pk=mandat_id)

    form = BoardMembershipForm(request.POST or None, mandat=mandat)

    if form.is_valid():
        instance = form.save(commit=False)
        instance.mandat = mandat
        instance.save()
        return redirect("mandat_detail", pk=mandat.id)

    return render(request, "backoffice/cms/governance/boardmembership_form.html", {
        "form": form,
        "mandat": mandat
    })
 
def boardmembership_update(request, pk):
    membership = get_object_or_404(BoardMembership, pk=pk)

    form = BoardMembershipForm(request.POST or None, instance=membership)

    if form.is_valid():
        form.save()
        return redirect("mandat_detail", pk=membership.mandat.id)

    return render(request, "backoffice/cms/governance/boardmembership_form.html",
     {
        "form": form,
        "mandat": membership.mandat
    })

def boardmembership_delete(request, pk):
    membership = get_object_or_404(BoardMembership, pk=pk)
    mandat_id = membership.mandat.id

    if request.method == "POST":
        membership.delete()
        return redirect("mandat_detail", pk=mandat_id)

    return render(request, "backoffice/cms/governance/confirm_delete.html", {
        "membership": membership
    }) 
 
def boardrole_list(request):
    roles = BoardRole.objects.all()
    return render(request, "backoffice/cms/governance/boardrole_list.html", {
        "roles": roles
    })

def boardrole_create(request):
    form = BoardRoleForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect("boardrole_list")

    return render(request, "backoffice/cms/governance/boardrole_form.html", {
        "form": form,
        "title": "Créer une fonction"
    })

def boardrole_update(request, pk):
    role = get_object_or_404(BoardRole, pk=pk)
    form = BoardRoleForm(request.POST or None, instance=role)

    if form.is_valid():
        form.save()
        return redirect("boardrole_list")

    return render(request, "backoffice/cms/governance/boardrole_form.html", {
        "form": form,
        "title": "Modifier la fonction"
    })
 
def boardrole_toggle(request, pk):
    role = get_object_or_404(BoardRole, pk=pk)
    role.actif = not role.actif
    role.save()
    return redirect("boardrole_list")