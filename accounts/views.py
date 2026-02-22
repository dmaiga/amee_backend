
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from accounts.models import User
from accounts.serializers import (
        UserMeSerializer,RegisterSerializer,
        CustomTokenObtainPairSerializer,
        LoginResponseSerializer,
        RegisterResponseSerializer
    )

from drf_spectacular.utils import extend_schema

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.shortcuts import redirect


from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect




@extend_schema(
    responses=UserMeSerializer,
    tags=["Accounts"],
)
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data)


@extend_schema(
    tags=["Authentication"],
    request=RegisterSerializer,
    responses=RegisterResponseSerializer,
)
class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

@extend_schema(
    tags=["Authentication"],
    request=RegisterSerializer,
    responses=RegisterResponseSerializer,
)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "status_code": 201,
                "message": "Utilisateur créé avec succès",
                "user": UserMeSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )