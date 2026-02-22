from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404

from interactions.models import ContactRequest
from quality_control.models import Feedback
from quality_control.serializers import FeedbackSerializer
from drf_spectacular.utils import extend_schema

@extend_schema(
    tags=["Quality Control"],
    request=FeedbackSerializer,
    responses=FeedbackSerializer,
)
class CreateFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        contact = get_object_or_404(ContactRequest, pk=pk)

        # ✅ seul le client concerné
        if contact.client != request.user:
            raise PermissionDenied(
                "Vous ne pouvez pas évaluer cette mission."
            )

        # ✅ mission terminée uniquement
        if contact.statut != "MISSION_TERMINEE":
            raise ValidationError(
                "Le feedback est possible uniquement après la fin de mission."
            )

        # ✅ éviter double feedback
        if hasattr(contact, "feedback"):
            raise ValidationError(
                "Un feedback existe déjà pour cette mission."
            )

        serializer = FeedbackSerializer(
            data=request.data,
            context={"request": request}
        )
        
        serializer.is_valid(raise_exception=True)
        
        serializer.save(contact_request=contact)
        


        return Response(serializer.data, status=201)
