from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.generics import RetrieveAPIView

from roster.models import ConsultantProfile
from roster.serializers import ConsultantPublicSerializer, ConsultantSerializer
from roster.permissions import EstBureauOuSuperAdmin


class SoumettreCandidatureView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        user = request.user

        # Vérifier adhésion active
        if not hasattr(user, 'adhesion') or not user.adhesion.est_actif:
            return Response(
                {"detail": "Adhésion non active."},
                status=status.HTTP_403_FORBIDDEN
            )

        if hasattr(user, 'profil_roster'):
            return Response(
                {"detail": "Profil déjà existant."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ConsultantSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=user, statut='SOUMIS')
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ValiderCandidatureView(APIView):
    permission_classes = [EstBureauOuSuperAdmin]

    def post(self, request, pk):

        profil = get_object_or_404(ConsultantProfile, pk=pk)

        if profil.statut != 'SOUMIS':
            return Response(
                {"detail": "Profil non soumis."},
                status=status.HTTP_400_BAD_REQUEST
            )

        profil.valider(validateur=request.user)

        return Response(
            {"detail": "Candidature validée."},
            status=status.HTTP_200_OK
        )

class MonProfilRosterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            profil = request.user.profil_roster
        except ConsultantProfile.DoesNotExist:
            return Response({
                "a_un_profil": False
            })

        serializer = ConsultantSerializer(profil)

        return Response({
            "a_un_profil": True,
            "statut": profil.statut,
            "est_consultant": request.user.role == 'CONSULTANT',
            "profil": serializer.data
        })



class ListeConsultantsPublicView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ConsultantPublicSerializer

    def get_queryset(self):
        return ConsultantProfile.objects.filter(
            statut='VALIDE',
            user__role='CONSULTANT'
        )



class DetailConsultantPublicView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = ConsultantPublicSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return ConsultantProfile.objects.filter(
            statut='VALIDE',
            user__role='CONSULTANT'
        )
