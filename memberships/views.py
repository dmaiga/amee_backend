from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .serializers import MembershipRegistrationSerializer


class MembershipRegistrationView(APIView):

    def post(self, request):

        serializer = MembershipRegistrationSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message":
                "Votre candidature a été envoyée. "
                "Elle sera analysée par le bureau et vous serez contacté par email."
            },
            status=status.HTTP_201_CREATED
        )