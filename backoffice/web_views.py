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

from django.db.models import Prefetch,Sum,Count, Q,Max

from django.core.mail import send_mail
from django.contrib import messages


from backoffice.api.tresorerie.services import TresorerieService
from backoffice.permissions.roster import can_manage_roster

from accounts.models import User
from roster.models import ConsultantProfile
from missions.models import Mission
from interactions.models import ContactRequest
from cms.models import Article, Resource, Opportunity

from quality_control.models import Feedback,IncidentReview


from tresorerie.models import Transaction

from backoffice.forms import (
    ArticleForm,ResourceForm,
    OpportunityForm,AffecterIncidentForm,
    StatuerIncidentForm, EnrolementPaiementForm)

from organizations.models import Organization
from memberships.models import Membership

from organizations.models import Organization

from backoffice.forms import OrganizationForm

from datetime import timedelta
from django.utils import timezone

from backoffice.service_paiement import PaiementService
from tresorerie.services import TresorerieService
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

from tresorerie.forms import EnrolementPaiementForm

User = get_user_model()

#-----------------------------
#
#-----------------------------

 
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
                    transactions__categorie="COTISATION",
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
def paiement_bureau(request, organisation_id=None):

    organisations = Organization.objects.filter(est_actif=True).order_by("nom")

    if request.method == "POST":

        organisation = get_object_or_404(
            Organization,
            pk=request.POST.get("organisation")
        )

        PaiementService.payer_organisation(
            user=request.user,
            organisation=organisation,
            operation=request.POST.get("operation"),
            montant=int(request.POST.get("montant")),
            description=request.POST.get("description"),
        )

        messages.success(request, "Paiement enregistré.")
        return redirect("bo_enrolement_dashboard")

    return render(
        request,
        "backoffice/tresorerie/paiement_bureau.html",
        {"organisations": organisations}
    )

@login_required
def tresorerie_paiement(request):

    if request.method == "GET":
        token = str(uuid.uuid4())
        request.session["paiement_token"] = token

        return render(
            request,
            "backoffice/tresorerie/tresorerie_form.html",
            {
                "form": EnrolementPaiementForm(),
                "paiement_token": token,
            },
        )

    form = EnrolementPaiementForm(request.POST)

    if not form.is_valid():
        return render(request,
                      "backoffice/tresorerie/tresorerie_form.html",
                      {"form": form})

    # anti double
    if request.POST.get("paiement_token") != request.session.get("paiement_token"):
        messages.warning(request, "Paiement déjà traité.")
        return redirect("bo_enrolement_dashboard")

    data = form.cleaned_data

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

    PaiementService.payer_membre(
        user=request.user,
        membre=membre,
        operation=data["operation"],
        data=data,
    )

    messages.success(request, "Enrôlement enregistré.")
    return redirect("bo_enrolement_dashboard")


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

    return render(
        request,
        "backoffice/clients/client_detail.html",
        {
            "client": client
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

    statut = request.GET.get("statut")

    articles = Article.objects.all().order_by("-date_publication")

    if statut == "publie":
        articles = articles.filter(publie=True)

    elif statut == "brouillon":
        articles = articles.filter(publie=False)

    return render(
        request,
        "backoffice/cms/articles/articles_list.html",
        {
            "articles": articles,
            "selected_statut": statut,
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
            form.save()
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

    categorie = request.GET.get("categorie")

    ressources = Resource.objects.all().order_by("-cree_le")

    if categorie:
        ressources = ressources.filter(categorie=categorie)

    return render(
        request,
        "backoffice/cms/ressources/ressources_list.html",
        {
            "ressources": ressources,
            "categories": Resource.CATEGORIE_CHOICES,
            "selected_categorie": categorie,
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
            form.save()
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
            form.save()
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

    organisations = (
        Organization.objects
        .annotate(
            derniere_cotisation=Max(
                "transactions__date_transaction",
                filter=Q(
                    transactions__categorie="COTISATION",
                    transactions__statut="VALIDEE"
                )
            )
        )
        .order_by("nom")
    )

    return render(
        request,
        "backoffice/organisations/organisations_list.html",
        {"organisations": organisations}
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
        form = OrganizationForm(request.POST, instance=organisation)

        if form.is_valid():
            organisation = form.save()

            messages.success(
                request,
                "Organisation enregistrée."
            )

            # 👉 redirection vers paiement
            return redirect(
                "bo_paiement_bureau_org",
                organisation_id=organisation.id
            )
    else:
        form = OrganizationForm(instance=organisation)

    return render(
        request,
        "backoffice/organisations/organisation_form.html",
        {"form": form}
    )