from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from drf_spectacular.utils import extend_schema

from .serializers import EnregistrerPaiementSerializer
from .services import TresorerieService
from backoffice.permissions.roles import IsCompta


@extend_schema(tags=["Tresorerie"])
class EnregistrerPaiementAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsCompta]
    serializer_class = EnregistrerPaiementSerializer

    def post(self, request):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        transaction = TresorerieService.enregistrer_paiement(
            user=request.user,
            data=serializer.validated_data
        )

        return Response(
            {
                "message": "Paiement enregistré et validé",
                "transaction_id": transaction.id,
                "statut": transaction.statut,
            },
            status=status.HTTP_201_CREATED,
        )