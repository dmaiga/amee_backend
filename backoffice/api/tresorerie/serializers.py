from rest_framework import serializers


class EnregistrerPaiementSerializer(serializers.Serializer):

    type_transaction = serializers.ChoiceField(
        choices=["ENTREE", "SORTIE"]
    )

    categorie = serializers.CharField()
    montant = serializers.IntegerField()

    email_payeur = serializers.EmailField(
        required=False,
        allow_null=True
    )

    membre_id = serializers.IntegerField(
        required=False,
        allow_null=True
    )

    description = serializers.CharField(
        required=False,
        allow_blank=True
    )

    date_transaction = serializers.DateField(required=False)
