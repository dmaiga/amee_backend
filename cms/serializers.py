from rest_framework import serializers
from cms.models import Article, Resource, Opportunity
from rest_framework import serializers



class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = "__all__"


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = "__all__"


class OpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = "__all__"


from rest_framework import serializers
from cms.models import Mandat, BoardMembership

from rest_framework import serializers
from cms.models import Mandat, BoardMembership

class BoardMemberSerializer(serializers.Serializer):
    poste = serializers.CharField(source="role.titre")
    nom = serializers.CharField(source="membership.user.last_name")
    prenom = serializers.CharField(source="membership.user.first_name")
    photo = serializers.SerializerMethodField()

    def get_photo(self, obj):
        request = self.context.get("request")
        user = obj.membership.user

        if user.photo:
            if request:
                return request.build_absolute_uri(user.photo.url)
            return user.photo.url

        return None

class MandatActifSerializer(serializers.ModelSerializer):
    president = serializers.SerializerMethodField()
    membres = serializers.SerializerMethodField()

    class Meta:
        model = Mandat
        fields = [
            "nom",
            "date_debut",
            "date_fin",
            "mot_president",
            "president",
            "membres",
        ]

    def get_president(self, obj):
        president = (
            BoardMembership.objects
            .filter(
                mandat=obj,
                role__titre__icontains="président"
            )
            .select_related("membership__user", "role")
            .first()
        )

        if president:
            return BoardMemberSerializer(president).data

        return None

    def get_membres(self, obj):
        membres = (
            BoardMembership.objects
            .filter(mandat=obj)
            .exclude(role__titre__icontains="président")
            .select_related("membership__user", "role")
            .order_by("role__ordre")
        )

        return BoardMemberSerializer(membres, many=True).data