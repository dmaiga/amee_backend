from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView
)
from rest_framework.permissions import IsAuthenticated
from missions.models import Mission
from missions.permissions import IsClient
from missions.serializers import MissionSerializer


class MissionCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsClient]
    serializer_class = MissionSerializer

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

class MesMissionsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MissionSerializer

    def get_queryset(self):
        return Mission.objects.filter(
            client=self.request.user
        ).order_by('-cree_le')

class MissionDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MissionSerializer

    def get_queryset(self):
        return Mission.objects.filter(
            client=self.request.user
        )
