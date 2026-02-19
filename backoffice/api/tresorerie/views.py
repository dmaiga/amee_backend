from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import EnregistrerPaiementSerializer
from .services import TresorerieService
from backoffice.permissions.roles import IsCompta


class EnregistrerPaiementAPIView(APIView):

    permission_classes = [IsAuthenticated, IsCompta]

    def post(self, request):

        serializer = EnregistrerPaiementSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        transaction = TresorerieService.enregistrer_paiement(
            user=request.user,
            data=serializer.validated_data
        )

        return Response({
            "message": "Paiement enregistré et validé",
            "transaction_id": transaction.id,
            "statut": transaction.statut
        })
