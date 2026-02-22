from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from memberships.models import Membership
from memberships.serializers import AdhesionSerializer,MonAdhesionResponseSerializer

from drf_spectacular.utils import extend_schema



@extend_schema(
    tags=["Memberships"],
    responses=MonAdhesionResponseSerializer,
)
class MonAdhesionView(APIView):
    permission_classes = [IsAuthenticated]
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
 
