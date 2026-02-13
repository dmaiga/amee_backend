from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from memberships.models import Membership
from memberships.permissions import EstComptaOuSuperAdmin
from memberships.serializers import AdhesionSerializer


class DemandeAdhesionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        if hasattr(request.user, 'adhesion'):
            return Response(
                {"detail": "Une demande d’adhésion existe déjà."},
                status=status.HTTP_400_BAD_REQUEST
            )

        Membership.objects.create(user=request.user)

        return Response(
            {"detail": "Demande d’adhésion créée avec succès."},
            status=status.HTTP_201_CREATED
        )

class MonAdhesionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            adhesion = request.user.adhesion
        except Membership.DoesNotExist:
            return Response({"a_une_adhesion": False})

        serializer = AdhesionSerializer(adhesion)

        return Response({
            "a_une_adhesion": True,
            "adhesion": serializer.data
        })
 
class ValidationAdhesionView(APIView):
    permission_classes = [EstComptaOuSuperAdmin]

    def post(self, request, pk):

        adhesion = get_object_or_404(Membership, pk=pk)

        if adhesion.statut == 'ACTIF':
            return Response(
                {"detail": "Cette adhésion est déjà active."},
                status=status.HTTP_400_BAD_REQUEST
            )

        adhesion.activer(valide_par=request.user)

        return Response(
            {"detail": "Adhésion validée avec succès."},
            status=status.HTTP_200_OK
        )
