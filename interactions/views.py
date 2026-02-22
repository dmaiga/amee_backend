from django.utils import timezone
from datetime import timedelta
from django.db import IntegrityError
from django.shortcuts import get_object_or_404

from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    GenericAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework import status

from interactions.models import ContactRequest
from interactions.serializers import (
    ContactRequestSerializer,
    ContactRequestReadSerializer,
    UpdateContactStatusSerializer,
    UpdateContactStatusResponseSerializer,
    SimpleMessageSerializer,
)

from roster.permissions import EstBureauOuSuperAdmin


# =====================================================
# CREATE CONTACT REQUEST
# =====================================================

class RequestContactView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ContactRequestSerializer

    def perform_create(self, serializer):

        mission = serializer.validated_data["mission"]
        profil = serializer.validated_data["consultant"]

        if mission.client != self.request.user:
            raise ValidationError("Mission invalide.")

        if profil.statut != "VALIDE":
            raise ValidationError("Consultant non approuvé.")

        if not profil.est_disponible:
            raise ValidationError("Consultant actuellement indisponible.")

        if profil.user.statut_qualite in ["SUSPENDU", "BANNI"]:
            raise ValidationError(
                "Ce consultant n'est actuellement pas disponible."
            )

        duree = serializer.validated_data.get(
            "duree_estimee_jours",
            mission.duree_estimee_jours,
        )

        date_suivi = None
        if duree:
            date_suivi = timezone.now() + timedelta(days=duree + 3)

        try:
            serializer.save(
                client=self.request.user,
                date_suivi_prevu=date_suivi,
            )
        except IntegrityError:
            raise ValidationError(
                "Vous avez déjà contacté ce consultant pour cette mission."
            )


# =====================================================
# LISTES
# =====================================================

class ConsultantInteractionsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ContactRequestReadSerializer

    def get_queryset(self):
        return ContactRequest.objects.filter(
            consultant=self.request.user
 
        ).select_related("mission", "client").order_by("-cree_le")


class ClientInteractionsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ContactRequestReadSerializer

    def get_queryset(self):
        return ContactRequest.objects.filter(
            client=self.request.user
        ).select_related("mission", "consultant").order_by("-cree_le")


# =====================================================
# UPDATE STATUS
# =====================================================

class UpdateContactStatusView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateContactStatusSerializer

    def patch(self, request, pk):

        contact = get_object_or_404(ContactRequest, pk=pk)

        if contact.consultant != request.user:
            raise PermissionDenied(
                "Vous ne pouvez pas modifier cette demande."
            )

        if contact.statut == "MISSION_CONFIRME":
            raise ValidationError("La mission est déjà confirmée.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        contact.statut = serializer.validated_data["statut"]
        contact.save()

        return Response(
            UpdateContactStatusResponseSerializer(
                {
                    "detail": "Statut mis à jour avec succès.",
                    "statut": contact.statut,
                    
                }
            ).data
        )


# =====================================================
# TERMINER MISSION
# =====================================================

class TerminerMissionView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SimpleMessageSerializer

    def patch(self, request, pk):

        contact = get_object_or_404(ContactRequest, pk=pk)

        if contact.consultant != request.user:
            raise PermissionDenied("Action non autorisée.")

        if contact.statut != "MISSION_CONFIRME":
            raise ValidationError(
                "La mission doit être confirmée avant d'être terminée."
            )

        contact.statut = "MISSION_TERMINEE"
        contact.save()

        contact.mission.statut = "FERMEE"
        contact.mission.save()

        return Response(
            self.get_serializer(
                {"detail": "Mission marquée comme terminée."}
            ).data
        )


# =====================================================
# SUIVI TERRAIN
# =====================================================

class SuiviMissionView(GenericAPIView):
    permission_classes = [EstBureauOuSuperAdmin]
    serializer_class = SimpleMessageSerializer

    def patch(self, request, pk):

        contact = get_object_or_404(ContactRequest, pk=pk)

        contact.suivi_effectue = True
        contact.date_suivi_reel = timezone.now()
        contact.save()

        return Response(
            self.get_serializer(
                {"detail": "Suivi terrain enregistré."}
            ).data
        )