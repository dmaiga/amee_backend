# --- DJANGO ---
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.db.models import Count,Q,Exists, OuterRef
from django.views.generic import CreateView
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils.timesince import timesince
from django.contrib import messages

from django.db import IntegrityError
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login

from portals.decorators import portal_access_required
from portals.mixins import PortalAccessMixin
from django.db.models import Count, Sum
from django.utils import timezone


# --- DJANGO REST FRAMEWORK ---
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from portals.serializers import ClientRegistrationSerializer



# --- APPS LOCALES (AMEE) ---
from accounts.models import User
from roster.models import ConsultantProfile
from missions.models import Mission, MissionDocument,MissionApplication
from interactions.models import ContactRequest
from quality_control.models import Feedback

from cms.models import Opportunity,Resource,Article

from roster.forms import ConsultantApplicationForm

from missions.forms import MissionCreateForm,MissionApplicationForm

from quality_control.forms import FeedbackForm
from portals.forms import ClientProfileForm
from memberships.forms import MemberEditForm
from django.db.models import Q

# ==========================================
# 1. AUTHENTIFICATION COMMUNE
# ==========================================

class ClientRegistrationAPIView(CreateAPIView):
    serializer_class = ClientRegistrationSerializer
    permission_classes = [AllowAny]

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

def plateforme_login(request):
    if request.user.is_authenticated:
        # Évite que quelqu'un déjà connecté ne repasse par le login
        return redirect_user_by_role(request.user)

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user:
            login(request, user)
            return redirect_user_by_role(user)
        
        return render(
            request, 
            "auth/login.html", 
            {"error": "Identifiants invalides"}
        )

    return render(request, "auth/login.html")

def redirect_user_by_role(user):
    """
    Fonction utilitaire pour centraliser la logique de redirection
    """
    # 1. Le client va sur son interface dédiée
    if user.role == "CLIENT":
        return redirect("client-dashboard")

    # 2. Les Membres et Consultants vont sur le portail unique /espace/

    if user.role in ["CONSULTANT", "MEMBER"]:
        return redirect("portal_dashboard")

    # 3. Le Staff (Admin, Compta, etc.) va vers le Backoffice
    if user.is_staff or user.role in ["ADMIN", "BUREAU", "SECRETARIAT"]:
        return redirect("bo_dashboard")

    # Fallback par défaut
    return redirect("login")

def plateforme_logout(request):
    logout(request)
    return redirect("login")
  
# ###########################################
#
# 2. ESPACE CLIENT (Institutions/Recruteurs)
#
# ###########################################

# ==========================================
#  CLIENT DASHBBOARD
# ==========================================

@login_required
@portal_access_required("client")
def client_dashboard(request):

    missions = (
        Mission.objects
        .filter(client=request.user)
        .annotate(
            nb_contacts=Count("contacts", distinct=True),
            nb_acceptes=Count(
                "contacts",
                filter=Q(contacts__statut="MISSION_CONFIRME"),
                distinct=True,
            ),
            nb_documents=Count("documents", distinct=True),
        )
        .order_by("-cree_le")
    )
    # -------------------------
    # KPI rapides
    # -------------------------

    missions_actives = missions.exclude(statut="TERMINEE").count()

    demandes_en_attente = ContactRequest.objects.filter(
        mission__client=request.user,
        statut="ENVOYE"
    ).count()

    collaborations_actives = ContactRequest.objects.filter(
        mission__client=request.user,
        statut="MISSION_CONFIRME"
    ).count()

    feedbacks_en_attente = ContactRequest.objects.filter(
        mission__client=request.user,
        statut="MISSION_TERMINEE",
        feedback__isnull=True
    ).count()

    # activité récente
    derniers_contacts = (
        ContactRequest.objects
        .filter(mission__client=request.user)
        .select_related("mission", "consultant")
        .order_by("-cree_le")[:5]
    )

    return render(
        request,
        "clients/dashboard.html",
        {
            "missions": missions[:5],
            "missions_actives": missions_actives,
            "demandes_en_attente": demandes_en_attente,
            "collaborations_actives": collaborations_actives,
            "feedbacks_en_attente": feedbacks_en_attente,
            "derniers_contacts": derniers_contacts,
        },
    )

# ================================
#  Gestion des Missions (Besoins)
#=================================

class ClientMissionCreateView(PortalAccessMixin,LoginRequiredMixin, CreateView):
  
    access_level = "client"
    model = Mission
    form_class = MissionCreateForm
    template_name = "clients/missions/create_mission.html"

    def form_valid(self, form):
        form.instance.client = self.request.user
        if form.instance.type_publication == "PUBLIQUE":
            form.instance.publie_le = timezone.now()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "client_mission_detail",
            kwargs={"pk": self.object.id},
        )
    
@login_required
@portal_access_required("client")
def mission_close(request, pk):

    mission = get_object_or_404(
        Mission,
        pk=pk,
        client=request.user
    )

    mission.statut = "TERMINEE"
    mission.save()

    return redirect("client_mission_detail", pk=pk)

class ClientMissionListView(PortalAccessMixin, LoginRequiredMixin, ListView):

    access_level = "client"
    template_name = "clients/missions/liste_missions.html"
    context_object_name = "missions"

    def get_queryset(self):
        return (
            Mission.objects
            .filter(client=self.request.user)
            .annotate(
                nb_contacts=Count("contacts"),
                nb_applications=Count("applications")
            )
            .order_by("-cree_le")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        missions = context["missions"]

        context["today"] = timezone.now().date()

        # total candidatures
        context["total_applications"] = sum(
            mission.nb_applications for mission in missions
        )

        # missions actives
        context["missions_actives"] = missions.filter(statut="ACTIVE").count()

        return context

class ClientMissionDetailView(PortalAccessMixin,LoginRequiredMixin, DetailView):
   
    access_level = "client"
    template_name = "clients/missions/detail_mission.html"
    model = Mission
    context_object_name = "mission"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        mission = self.object
       
        historique = []

        # création mission
        historique.append({
            "date": mission.cree_le,
            "label": "Mission créée",
        })

        # demandes envoyées
        for contact in mission.contacts.all():
            historique.append({
                "date": contact.cree_le,
                "label": f"Demande envoyée à {contact.consultant.get_full_name()}",
            })

            if contact.statut == "MISSION_CONFIRME":
                historique.append({
                    "date": contact.cree_le,
                    "label": f"{contact.consultant.get_full_name()} a accepté",
                })

            if contact.statut == "MISSION_TERMINEE":
                historique.append({
                    "date": contact.cree_le,
                    "label": "Mission terminée",
                })

        # documents
        for doc in mission.documents.all():
            historique.append({
                "date": doc.cree_le,
                "label": f"Document ajouté : {doc.nom}",
            })

        context["historique"] = sorted(
            historique,
            key=lambda x: x["date"],
            reverse=True
        )

        applications = mission.applications.select_related("consultant")

        context["applications"] = applications
        context["applications_attente"] = applications.filter(statut="EN_ATTENTE")
        context["applications_retenues"] = applications.filter(statut="RETENU")
        context["applications_refusees"] = applications.filter(statut="REFUSE")
        return context

    def get_queryset(self):
        return (
            Mission.objects
            .filter(client=self.request.user)
            .prefetch_related(
                "documents",
                "contacts__consultant",
            )
        )

@login_required
@portal_access_required("client")
def detail_postulation_consultant(request, pk):

    application = get_object_or_404(
        MissionApplication.objects.select_related("consultant"),
        pk=pk,
        mission__client=request.user
    )

    return render(
        request,
        "clients/missions/detail_postulation_consultant.html",
        {
            "application": application,
            "consultant": application.consultant,
            "mission": application.mission,
        }
    )


@login_required
@portal_access_required("client")
def mission_add_document(request, mission_id):

    mission = get_object_or_404(
        Mission,
        id=mission_id,
        client=request.user
    )

    if request.method == "POST" and request.FILES.get("fichier"):

        MissionDocument.objects.create(
            mission=mission,
            fichier=request.FILES["fichier"],
            nom=request.POST.get("nom") or request.FILES["fichier"].name,
            type_document=request.POST.get("type_document", "AUTRE"),
            upload_par=request.user,
        )

    return redirect("client_mission_detail", pk=mission.id)

@login_required
@portal_access_required("client")
def application_update_status(request, pk, action):

    application = get_object_or_404(
        MissionApplication,
        pk=pk,
        mission__client=request.user
    )

    if action == "retenu":
        application.statut = "RETENU"
    elif action == "refuse":
        application.statut = "REFUSE"

    application.save()

    return redirect("client_mission_detail", pk=application.mission.pk) 



# ================================
#  Roster & Experts (Vue Client)
#=================================
   
class ExpertListView(PortalAccessMixin,LoginRequiredMixin, ListView):
    
    access_level = "client"
    template_name = "clients/experts/liste_experts.html"
    context_object_name = "experts"

    def get_queryset(self):

        client = self.request.user

        collaborations = ContactRequest.objects.filter(
            mission__client=client,
            consultant=OuterRef("user"),
            statut__in=["MISSION_CONFIRME", "MISSION_TERMINEE"],
        )

        queryset = (
            ConsultantProfile.objects
            .select_related("user")
            .annotate(
                deja_collabore=Exists(collaborations)
            )
            .filter(
                statut="VALIDE",
                est_disponible=True,
                user__membership__isnull=False,
                user__statut_qualite__in=["NORMAL", "SURVEILLANCE"],
            )
            .order_by("-deja_collabore", "-date_validation")
        )

        # ---------------- FILTERS ----------------

        filtre = self.request.GET.get("filtre")

        if filtre == "connus":
            queryset = queryset.filter(deja_collabore=True)

        elif filtre == "nouveaux":
            queryset = queryset.filter(deja_collabore=False)

        localisation = self.request.GET.get("localisation")

        if localisation:
            queryset = queryset.filter(
                public_profile__localisation__icontains=localisation
            )

        return queryset
   
class ClientExpertDetailView(PortalAccessMixin,LoginRequiredMixin, DetailView):
    
    access_level = "client"
    template_name = "clients/experts/detail_expert.html"
    context_object_name = "expert"
    model = ConsultantProfile
    pk_url_kwarg = "consultant_id"

    def get_queryset(self):

        client = self.request.user

        collaborations = ContactRequest.objects.filter(
            mission__client=client,
            consultant=OuterRef("user"),
            statut__in=["MISSION_CONFIRME", "MISSION_TERMINEE"],
        )

        return (
            ConsultantProfile.objects
            .select_related("user")
            .annotate(
                deja_collabore=Exists(collaborations)
            )
            .filter(
                statut="VALIDE",
                est_disponible=True,
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        expert_user = self.object.user

        context["missions_client"] = (
            self.request.user.missions
            .all()
            .order_by("-cree_le")
        )

        # nombre collaborations
        context["nb_collaborations"] = (
            ContactRequest.objects.filter(
                mission__client=self.request.user,
                consultant=expert_user,
                statut__in=["MISSION_CONFIRME", "MISSION_TERMINEE"],
            ).count()
        )

        return context


# ==========================================
# Interactions & Collaborations
# ==========================================

@login_required
@portal_access_required("client")
def request_contact_client(request):

    if request.method != "POST":
        return redirect("client_missions")

    mission_id = request.POST.get("mission_id")
    consultant_id = request.POST.get("consultant_id")
    message = request.POST.get("message", "")

    mission = get_object_or_404(
        Mission,
        id=mission_id,
        client=request.user
    )

    profil = get_object_or_404(
        ConsultantProfile,
        id=consultant_id,
        statut="VALIDE",
        est_disponible=True,
    )

    try:
        ContactRequest.objects.create(
            client=request.user,
            consultant=profil.user,
            mission=mission,
            message=message,
            initie_par="CLIENT",
        )
    except IntegrityError:
        messages.warning(
            request,
            "Vous avez déjà contacté cet expert pour cette mission."
        )

    return redirect("client_mission_detail", pk=mission.id)

@login_required
@portal_access_required("client")
def client_collaborations(request):

    contacts = (
        ContactRequest.objects
        .filter(
            mission__client=request.user
        )
        .select_related(
            "mission",
            "consultant",
            "consultant__profil_roster",
        )
    )

    applications = (
        MissionApplication.objects
        .filter(
            mission__client=request.user,
            statut="RETENU"
        )
        .select_related(
            "mission",
            "consultant"
        )
    )

    missions = request.user.missions.all().order_by("-cree_le")

    return render(
        request,
        "clients/collaborations/collaborations.html",
        {
            "contacts": contacts,
            "applications": applications,
            "missions": missions,
        },
    )

@login_required
@portal_access_required("client")
def relancer_consultant(request, pk):

    contact = get_object_or_404(
        ContactRequest,
        pk=pk,
        mission__client=request.user,
    )

    # uniquement si en attente
    if contact.statut != "ENVOYE":
        messages.warning(
            request,
            "Cette demande ne peut plus être relancée."
        )
        return redirect("client_collaborations")

    # -------------------------
    # Anti spam : 48h
    # -------------------------
    if contact.date_derniere_relance:

        delta = timezone.now() - contact.date_derniere_relance
        limite = 172800  # 48h en secondes

        if delta.total_seconds() < limite:

            reste = limite - delta.total_seconds()
            heures_restantes = int(reste // 3600)

            messages.warning(
                request,
                f"Relance déjà envoyée. "
                f"Vous pourrez relancer à nouveau dans environ "
                f"{heures_restantes} h."
            )

            return redirect("client_collaborations")

    # -------------------------
    # Envoi relance
    # -------------------------
    contact.date_derniere_relance = timezone.now()
    contact.nb_relances += 1
    contact.save()

    contact.consultant.email_user(
        subject="Rappel – Demande AMEE en attente",
        message=f"""
Bonjour,

Une demande concernant la mission
« {contact.mission.titre} »
attend toujours votre réponse.

Merci de vous connecter à votre espace AMEE
pour accepter ou refuser cette collaboration.

Equipe AMEE
"""
    )

    messages.info(request, "Relance envoyée au consultant.")

    return redirect("client_collaborations")

# ==========================================
# Qualité (Feedback Client)
# ==========================================
@login_required
@portal_access_required("client")
def donner_feedback(request, pk, source):

    if source == "contact":

        contact = get_object_or_404(
            ContactRequest,
            pk=pk,
            client=request.user
        )

        if contact.statut != "MISSION_TERMINEE":
            messages.warning(
                request,
                "Le feedback est disponible uniquement après la fin de mission."
            )
            return redirect("client_collaborations")

        if hasattr(contact, "feedback"):
            messages.info(request, "Un feedback a déjà été soumis.")
            return redirect("client_collaborations")

        mission = contact.mission

    elif source == "application":

        application = get_object_or_404(
            MissionApplication,
            pk=pk,
            mission__client=request.user
        )

        if hasattr(application, "feedback"):
            messages.info(request, "Un feedback a déjà été soumis.")
            return redirect("client_collaborations")

        mission = application.mission

    if request.method == "POST":

        form = FeedbackForm(request.POST)

        if form.is_valid():

            feedback = form.save(commit=False)
            feedback.client = request.user

            if source == "contact":
                feedback.contact_request = contact
            else:
                feedback.application = application

            feedback.save()

            messages.success(request, "Merci pour votre évaluation.")
            return redirect("client_collaborations")

    else:
        form = FeedbackForm()

    return render(
        request,
        "clients/quality/feedback_form.html",
        {
            "form": form,
            "mission": mission,
        }
    )


@login_required
@portal_access_required("client")
def client_feedback_list(request):

    feedbacks = (
        Feedback.objects
        .filter(client=request.user)
        .select_related(
            "contact_request__mission",
            "contact_request__consultant",
            "application__mission",
            "application__consultant",
        )
        .order_by("-cree_le")
    )

    return render(
        request,
        "clients/quality/feedback_list.html",
        {"feedbacks": feedbacks},
    )

@login_required
@portal_access_required("client")
def client_feedback_detail(request, pk):

    feedback = get_object_or_404(
        Feedback,
        pk=pk,
        client=request.user
    )

    return render(
        request,
        "clients/quality/feedback_detail.html",
        {"feedback": feedback},
    )

# ======================================
#  Paramètres
# ======================================

@login_required
@portal_access_required("client")
def client_profile_settings(request):

    profile = request.user.client_profile

    if request.method == "POST":
        form = ClientProfileForm(request.POST, instance=profile)

        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour.")
            return redirect("client_profile_settings")
    else:
        form = ClientProfileForm(instance=profile)

    return render(
        request,
        "clients/profile/settings.html",
        {"form": form},
    )

# ==========================================
# 3. ESPACE MEMBRE  / CONSULTANT
# ==========================================

@login_required
@portal_access_required("member")
def portal_dashboard(request):

    user = request.user
    context = {}

    # -------------------------
    # ADHESION
    # -------------------------
    adhesion = getattr(user, "membership", None)

    context["membership"] = adhesion
    context["est_membre_actif"] = (
        adhesion.est_actif if adhesion else False
    )

    # -------------------------
    # CONSULTANT
    # -------------------------
    profil = getattr(user, "profil_roster", None)

    context["profil_roster"] = profil
    context["est_consultant_valide"] = (
        profil.est_actif_roster if profil else False
    )

    # -------------------------
    # KPI CONSULTANT
    # -------------------------

    if context["est_consultant_valide"]:
        context["nb_sollicitations"] = ContactRequest.objects.filter(
            consultant=user,
            statut="ENVOYE"
        ).count()

        context["nb_missions_actives"] = ContactRequest.objects.filter(
            consultant=user,
            statut="MISSION_CONFIRME"
        ).count()
    # -------------------------
    # CMS
    # -------------------------
    context["derniere_ressources"] = Resource.objects.order_by("-cree_le")[:3]
    context["opportunites"] = Opportunity.objects.order_by("-date_limite")[:3]

    return render(request, "membres/dashboard.html", context)

# ===============
# MISSION 
# ===============
class ConsultantMissionListView(PortalAccessMixin,LoginRequiredMixin, ListView):
    access_level = "member"
    template_name = "membres/missions/liste_missions_publiques.html"
    context_object_name = "missions"

    def get_queryset(self):
        return Mission.objects.filter(
            type_publication="PUBLIQUE",
            statut="ACTIVE",
        ).order_by("-publie_le")

class ConsultantMissionDetailView(
    PortalAccessMixin,
    LoginRequiredMixin,
    DetailView
):
    access_level = "member"
    model = Mission
    template_name = "membres/missions/detail_mission.html"
    context_object_name = "mission"

    def get_queryset(self):
        return Mission.objects.filter(
            type_publication="PUBLIQUE",
            statut="ACTIVE",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        mission = self.object

        application = MissionApplication.objects.filter(
            mission=mission,
            consultant=self.request.user
        ).first()

        context["application"] = application
        context["form"] = MissionApplicationForm()

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        mission = self.object

        # vérifier si déjà postulé
        if MissionApplication.objects.filter(
            mission=mission,
            consultant=request.user
        ).exists():
            messages.warning(request, "Vous avez déjà postulé.")
            return redirect("consultant_mission_detail", pk=mission.pk)

        form = MissionApplicationForm(request.POST, request.FILES)

        if form.is_valid():
            application = form.save(commit=False)
            application.mission = mission
            application.consultant = request.user
            application.save()

            messages.success(request, "Votre candidature a été envoyée.")
            return redirect("consultant_mission_detail", pk=mission.pk)

        # si form invalide → réafficher page avec erreurs
        context = self.get_context_data()
        context["form"] = form
        return self.render_to_response(context)
# ===============
# Profil Member
# ===============

@login_required
@portal_access_required("member")
def member_profile(request):

    consultant_profile = getattr(request.user, "profil_roster", None)

    return render(
        request,
        "membres/profile/profile.html",
        {
            "user": request.user,
            "consultant_profile": consultant_profile,
        }
    )

@login_required
@portal_access_required("member")
def edit_profile(request):

    if request.method == "POST":
        form = MemberEditForm(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour.")
            return redirect("member_profile")

    else:
        form = MemberEditForm(instance=request.user)

    return render(
        request,
        "membres/profile/edit_profile.html",
        {"form": form}
    )

# ===============
# Roster Member
# ===============

@login_required
@portal_access_required("member")
def roster_dashboard(request):

    profil = getattr(request.user, "profil_roster", None)

    context = {
        "profil": profil,
    }

    return render(
        request,
        "membres/roster/dashboard.html",
        context
    )

@login_required
@portal_access_required("member")
def roster_reexamen(request):

    profil = getattr(request.user, "profil_roster", None)

    if not profil or profil.statut != "REFUSE":
        return redirect("portal_dashboard")

    if request.method == "POST":

        motif = request.POST.get("motif")

        profil.demander_reexamen(
            demandeur=request.user,
            motif=motif
        )

        messages.success(
            request,
            "Votre demande de réexamen a été envoyée."
        )

        return redirect("portal_dashboard")

    return render(
        request,
        "membres/roster/reexamen.html",
        {"profil": profil}
    )

@login_required
@portal_access_required("member")
def roster_profile(request):

    profil, _ = ConsultantProfile.objects.get_or_create(
        user=request.user
    )

    form = ConsultantApplicationForm(
        request.POST or None,
        request.FILES or None,
        instance=profil
    )

    if request.method == "POST" and form.is_valid():
        form.save(request.user)

        messages.success(
            request,
            "Votre dossier a été enregistré."
        )
        return redirect("member_profile")

    return render(
        request,
        "membres/roster/form.html",
        {
            "form": form,
            "profil": profil,
        }
    )

# ===============
#  Membership
# ===============

from tresorerie.models import Transaction
from django.utils import timezone


@login_required
@portal_access_required("member")
def membership_detail(request):

    adhesion = getattr(request.user, "adhesion", None)

    paiements = Transaction.objects.filter(
        membre=request.user,
        statut="VALIDEE",
        categorie__in=["ADHESION", "COTISATION"],
    ).order_by("-date_transaction")

    statut = "INACTIF"
    expiration_proche = False

    if adhesion and adhesion.est_actif:
        statut = "ACTIF"

        if adhesion.date_expiration:
            delta = adhesion.date_expiration - timezone.now().date()
            expiration_proche = delta.days <= 30

    return render(
        request,
           "membres/membership/detail.html",
        {
            "adhesion": adhesion,
            "paiements": paiements,
            "statut": statut,
            "expiration_proche": expiration_proche,
        },
    )


@login_required
@portal_access_required("member")
def resources_list(request):

    ressources = Resource.objects.all().order_by("-cree_le")

    # si ressource réservée → membre actif seulement
    if not getattr(request.user, "adhesion", None) or not request.user.adhesion.est_actif:
        ressources = ressources.filter(reserve_aux_membres=False)

    return render(
        request,
        "membres/resources/list.html",
        {
            "ressources": ressources,
        },
    )



@login_required
@portal_access_required("member")
def events_list(request):

    events = Article.objects.filter(
        type__in=["EVENEMENT", "FORMATION"],
        publie=True,
    ).order_by("-date_publication")

    return render(
        request,
        "membres/events/list.html",
        {
            "events": events,
        },
    )




@login_required
@portal_access_required("member")
def opportunities_list(request):

    opportunities = Opportunity.objects.filter(
        publie=True
    ).order_by("-cree_le")

    return render(
        request,
        "membres/opportunities/list.html",
        {
            "opportunities": opportunities,
        }
    )

@login_required
@portal_access_required("member")
def opportunity_detail(request, pk):

    opportunity = get_object_or_404(
        Opportunity,
        pk=pk,
        publie=True
    )

    return render(
        request,
        "membres/opportunities/detail.html",
        {
            "opportunity": opportunity,
        }
    )


@login_required
@portal_access_required("consultant")
def sollicitations_list(request):

    sollicitations = (
        ContactRequest.objects
        .filter(
            consultant=request.user,
            statut="ENVOYE"
        )
        .select_related("mission", "client")
        .order_by("-cree_le")
    )

    return render(
        request,
        "membres/sollicitations/list.html",
        {"sollicitations": sollicitations}
    )

@login_required
@portal_access_required("consultant")
def sollicitation_detail(request, pk):

    contact = get_object_or_404(
        ContactRequest.objects.select_related("mission")
        .prefetch_related("mission__documents"),
        pk=pk,
        consultant=request.user
    )

    if request.method == "POST":

        action = request.POST.get("action")

        if action == "accept":
            contact.statut = "MISSION_CONFIRME"

        elif action == "refuse":
            contact.statut = "REFUSE"

        contact.save()
        return redirect("sollicitations_list")

    return render(
        request,
        "membres/sollicitations/detail.html",
        {"contact": contact}
    )


@login_required
@portal_access_required("consultant")
def consultant_missions(request):

    missions = (
        ContactRequest.objects
        .filter(
            consultant=request.user,
            statut__in=[
                "MISSION_CONFIRME",
                "MISSION_TERMINEE"
            ]
        )
        .select_related("mission", "client")
        .order_by("-cree_le")
    )

    return render(
        request,
        "membres/missions/list.html",
        {"missions": missions}
    )


# membres/views.py


@login_required
@portal_access_required("consultant")
def mission_detail(request, pk):

    contact = get_object_or_404(
        ContactRequest.objects.select_related(
            "mission",
            "client"
        ).prefetch_related(
            "mission__documents"
        ),
        pk=pk,
        consultant=request.user
    )

    # sécurité
    if contact.statut not in [
        "MISSION_CONFIRME",
        "MISSION_TERMINEE"
    ]:
        return redirect("consultant_missions")

    # ACTIONS
    if request.method == "POST":

        action = request.POST.get("action")

        if action == "terminer":
            try:
                contact.terminer()
                messages.success(
                    request,
                    "Mission marquée comme terminée."
                )
            except ValueError:
                messages.warning(
                    request,
                    "Impossible de terminer cette mission."
                )

            return redirect("consultant_mission_detail", pk=contact.pk)

    return render(
        request,
        "membres/missions/detail.html",
        {
            "contact": contact,
            "mission": contact.mission,
        }
    )


