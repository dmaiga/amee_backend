# memberships/serializers.py

from rest_framework import serializers
from memberships.models import Membership


class AdhesionSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(source='user.email', read_only=True)
    id_membre = serializers.CharField(
        source='user.id_membre_association',
        read_only=True
    )
    est_actif = serializers.BooleanField(read_only=True)

    class Meta:
        model = Membership
        fields = [
            'email',
            'id_membre',
            'statut',
            'montant_paye',
            'date_paiement',
            'date_expiration',
            'est_actif'
        ]
