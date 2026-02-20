from rest_framework.generics import CreateAPIView,ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError

from django.utils import timezone
from datetime import timedelta
from django.db import IntegrityError
from django.shortcuts import get_object_or_404

from interactions.models import ContactRequest
from interactions.serializers import ContactRequestReadSerializer, ContactRequestSerializer,UpdateContactStatusSerializer

from roster.permissions import EstBureauOuSuperAdmin
from roster.models import ConsultantProfile

from missions.models import Mission



class RequestContactView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ContactRequestSerializer

    def perform_create(self, serializer):

        mission = serializer.validated_data["mission"]
        profil = serializer.validated_data["consultant"]

        # sécurité mission
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
            mission.duree_estimee_jours
        )

        date_suivi = None
        if duree:
            date_suivi = timezone.now() + timedelta(days=duree + 3)

        try:
            serializer.save(
                client=self.request.user,
                date_suivi_prevu=date_suivi
            )
        except IntegrityError:
            raise ValidationError(
                "Vous avez déjà contacté ce consultant pour cette mission."
            )


class ConsultantInteractionsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ContactRequestReadSerializer

    def get_queryset(self):
        return ContactRequest.objects.filter(
            consultant=self.request.user
        ).select_related(
            'mission', 'client'
        ).order_by('-cree_le')


class ClientInteractionsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ContactRequestReadSerializer

    def get_queryset(self):
        return ContactRequest.objects.filter(
            client=self.request.user
        ).select_related(
            'mission', 'consultant'
        ).order_by('-cree_le')


class UpdateContactStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):

        contact = get_object_or_404(ContactRequest, pk=pk)

        # 🔐 seul le consultant peut modifier
        if contact.consultant != request.user:
            raise PermissionDenied(
                "Vous ne pouvez pas modifier cette demande."
            )
        if contact.statut == "MISSION_CONFIRME":
            raise ValidationError(
                "La mission est déjà confirmée."
            )
        
        serializer = UpdateContactStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        nouveau_statut = serializer.validated_data['statut']

        contact.statut = nouveau_statut
        contact.save()

        return Response({
            "detail": "Statut mis à jour avec succès.",
            "statut": contact.statut
        })


class TerminerMissionView(APIView):
    permission_classes = [IsAuthenticated]

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
        
        mission = contact.mission
        mission.statut = "FERMEE"
        mission.save()

        return Response({
            "detail": "Mission marquée comme terminée."
        })


class SuiviMissionView(APIView):
    permission_classes = [EstBureauOuSuperAdmin]

    def patch(self, request, pk):

        contact = get_object_or_404(ContactRequest, pk=pk)

        contact.suivi_effectue = True
        contact.date_suivi_reel = timezone.now()
        contact.save()

        return Response({
            "detail": "Suivi terrain enregistré."
        })
