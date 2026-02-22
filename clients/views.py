# --- DJANGO ---
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.db.models import Count,Q
from django.views.generic import CreateView
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils.timesince import timesince
from django.contrib import messages
from django.db.models import Exists, OuterRef
from django.db import IntegrityError

# --- DJANGO REST FRAMEWORK ---
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny



# --- APPS LOCALES (AMEE) ---
from accounts.models import User
from roster.models import ConsultantProfile
from missions.models import Mission, MissionDocument
from missions.forms import MissionCreateForm
from clients.serializers import ClientRegistrationSerializer
from clients.decorators import client_required

from interactions.models import ContactRequest
from quality_control.forms import FeedbackForm
from quality_control.models import Feedback
from clients.forms import ClientProfileForm
 

class ClientRegistrationAPIView(CreateAPIView):
    serializer_class = ClientRegistrationSerializer
    permission_classes = [AllowAny]


@login_required
@client_required
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

##

class ClientMissionCreateView(LoginRequiredMixin, CreateView):
    model = Mission
    form_class = MissionCreateForm
    template_name = "clients/missions/create_mission.html"

    def form_valid(self, form):
        form.instance.client = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "client_mission_detail",
            kwargs={"pk": self.object.id},
        )
    
class ClientMissionListView(LoginRequiredMixin, ListView):
    template_name = "clients/missions/liste_missions.html"
    context_object_name = "missions"

    def get_queryset(self):
        return (
            Mission.objects
            .filter(client=self.request.user)
            .annotate(nb_contacts=Count("contacts"))
            .order_by("-cree_le")
        )

class ClientMissionDetailView(LoginRequiredMixin, DetailView):
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

##

class ExpertListView(LoginRequiredMixin, ListView):
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
            .select_related("user", "public_profile")
            .annotate(
                deja_collabore=Exists(collaborations)
            )
            .filter(
                statut="VALIDE",
                est_disponible=True,
                user__adhesion__isnull=False,
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
    
from django.db.models import Exists, OuterRef, Count
from interactions.models import ContactRequest


class ClientExpertDetailView(LoginRequiredMixin, DetailView):
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
            .select_related("user", "public_profile")
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

##


@login_required
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
        )
    except IntegrityError:
        messages.warning(
            request,
            "Vous avez déjà contacté cet expert pour cette mission."
        )

    return redirect("client_mission_detail", pk=mission.id)


@login_required
def client_collaborations(request):

    contacts = (
        ContactRequest.objects
        .filter(mission__client=request.user)
        .select_related(
            "mission",
            "consultant",
            "consultant__profil_roster",
        )
        .order_by("-cree_le")
    )

    # -----------------------
    # FILTRES
    # -----------------------

    statut = request.GET.get("statut")
    mission_id = request.GET.get("mission")

    if statut:
        contacts = contacts.filter(statut=statut)

    if mission_id:
        contacts = contacts.filter(mission_id=mission_id)

    missions = (
        request.user.missions
        .all()
        .order_by("-cree_le")
    )

    return render(
        request,
        "clients/collaborations/collaborations.html",
        {
            "contacts": contacts,
            "missions": missions,
            "selected_statut": statut,
            "selected_mission": mission_id,
        },
    )




@login_required
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

    messages.success(request, "Relance envoyée au consultant.")

    return redirect("client_collaborations")



@login_required
def donner_feedback(request, pk):

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

    if request.method == "POST":
        form = FeedbackForm(request.POST)

        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.client = request.user
            feedback.contact_request = contact
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
            "contact": contact,
        }
    )



@login_required
def client_feedback_list(request):

    feedbacks = (
        Feedback.objects
        .filter(client=request.user)
        .select_related(
            "contact_request__mission",
            "contact_request__consultant",
        )
        .order_by("-cree_le")
    )

    return render(
        request,
        "clients/quality/feedback_list.html",
        {"feedbacks": feedbacks},
    )

@login_required
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

#
#
#

@login_required
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