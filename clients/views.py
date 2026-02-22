# --- DJANGO ---
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.db.models import Count
from django.views.generic import CreateView
from django.urls import reverse

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




class ClientRegistrationAPIView(CreateAPIView):
    serializer_class = ClientRegistrationSerializer
    permission_classes = [AllowAny]

@login_required
@client_required
def client_dashboard(request):

    missions = Mission.objects.filter(
        client=request.user
    ).order_by("-cree_le")

    return render(
        request,
        "clients/dashboard.html",
        {"missions": missions}
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

        return (
            ConsultantProfile.objects
            .select_related("user", "public_profile")
            .filter(
                statut="VALIDE",
                est_disponible=True,
                user__adhesion__isnull=False,
                user__statut_qualite__in=["NORMAL", "SURVEILLANCE"],
            )
            .order_by("-date_validation")
        )

class ClientExpertDetailView(LoginRequiredMixin, DetailView):
    template_name = "clients/experts/detail_expert.html"
    context_object_name = "expert"
    model = ConsultantProfile
    pk_url_kwarg = "consultant_id"

    def get_queryset(self):
        return (
            ConsultantProfile.objects
            .select_related("user", "public_profile")
            .filter(
                statut="VALIDE",
                est_disponible=True,
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # missions du client pour sélection
        context["missions_client"] = (
            self.request.user.missions.all()
            .order_by("-cree_le")
        )

        return context

