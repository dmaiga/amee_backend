from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema

from roster.models import ConsultantProfile
from roster.permissions import EstBureauOuSuperAdmin
from roster.serializers import (
    ConsultantSerializer,
    ConsultantPublicSerializer,
    MessageResponseSerializer,
    MonProfilRosterResponseSerializer,
)


# ===============================
# SOUMETTRE CANDIDATURE
# ===============================

@extend_schema(tags=["Roster"])
class SoumettreCandidatureView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConsultantSerializer

    def post(self, request):

        user = request.user

        if not hasattr(user, "adhesion") or not user.adhesion.est_actif:
            return Response(
                {"detail": "Adhésion non active."},
                status=status.HTTP_403_FORBIDDEN,
            )

        profil = getattr(user, "profil_roster", None)

        if profil:
            if profil.statut == "REFUSE":
                profil.demander_reexamen(demandeur=user)
                return Response({"detail": "Demande de réexamen envoyée."})

            return Response(
                {"detail": "Une candidature est déjà en cours."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user, statut="SOUMIS")

        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ===============================
# VALIDER CANDIDATURE
# ===============================

@extend_schema(tags=["Roster"])
class ValiderCandidatureView(GenericAPIView):
    permission_classes = [EstBureauOuSuperAdmin]
    serializer_class = MessageResponseSerializer

    def post(self, request, pk):

        profil = get_object_or_404(ConsultantProfile, pk=pk)

        if profil.statut not in ["SOUMIS", "REFUSE"]:
            return Response(
                {"detail": "Profil non soumis."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profil.valider(validateur=request.user)

        return Response(
            self.get_serializer(
                {"detail": "Candidature validée."}
            ).data
        )


# ===============================
# MON PROFIL ROSTER
# ===============================

@extend_schema(tags=["Roster"])
class MonProfilRosterView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MonProfilRosterResponseSerializer

    def get(self, request):

        try:
            profil = request.user.profil_roster
        except ConsultantProfile.DoesNotExist:
            return Response({"a_un_profil": False})

        serializer = ConsultantSerializer(profil)

        return Response(
            {
                "a_un_profil": True,
                "statut": profil.statut,
                "est_consultant": request.user.role == "CONSULTANT",
                "profil": serializer.data,
            }
        )


# ===============================
# PUBLIC LIST
# ===============================

class ListeConsultantsPublicView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ConsultantPublicSerializer

    def get_queryset(self):
        return ConsultantProfile.objects.filter(
            statut="VALIDE",
            est_disponible=True,
            user__adhesion__date_expiration__gte=timezone.now().date(),
            user__statut_qualite__in=["NORMAL", "SURVEILLANCE"],
        )


class DetailConsultantPublicView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = ConsultantPublicSerializer

    def get_queryset(self):
        return ConsultantProfile.objects.filter(
            statut="VALIDE",
            est_disponible=True,
            user__adhesion__date_expiration__gte=timezone.now().date(),
            user__role="CONSULTANT",
            user__statut_qualite__in=["NORMAL", "SURVEILLANCE"],
        )