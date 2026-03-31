from rest_framework import serializers
from cms.models import Article,Resource, Opportunity,Photo,Gallery
from rest_framework import serializers



from rest_framework import serializers
from .models import Article
from rest_framework import serializers
from .models import Resource, Opportunity,Photo,Gallery

from rest_framework import serializers
from cms.models import Mandat, BoardMembership

from rest_framework import serializers
from cms.models import Mandat, BoardMembership
# serializers.py

from rest_framework import serializers
from .models import Gallery, Photo


# serializers.py

from rest_framework import serializers



class ArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = [
            'id', 'titre', 'slug', 'type', 'contenu', 
            'image', 'lectures', 'date_publication', 'lien_externe'
        ]


class PublicResourceSerializer(serializers.ModelSerializer):
    categorie_display = serializers.CharField(source='get_categorie_display', read_only=True)

    class Meta:
        model = Resource
        fields = [
            'id', 'titre_fr', 'titre_en', 
            'description_fr', 'description_en', 
            'slug_fr', 'slug_en',
            'fichier', 'categorie', 'categorie_display', 
            'cree_le'
        ]

class PublicOpportunitySerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    # On expose les propriétés calculées utiles pour l'UI
    est_expire = serializers.BooleanField(read_only=True)
    jours_restants = serializers.IntegerField(read_only=True)

    class Meta:
        model = Opportunity
        fields = [
            'id', 'titre_fr', 'titre_en', 
            'description_fr', 'description_en', 
            'slug_fr', 'slug_en',
            'type', 'type_display', 
            'date_limite', 'est_expire', 'jours_restants',
            'fichier_joint', 'lien_externe', 
            'cree_le'
        ]

class PhotoSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = ['id', 'image_url', 'uploaded_at'] 

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None
    
class GalleryListSerializer(serializers.ModelSerializer):
    
    photo_count = serializers.IntegerField(read_only=True)
    cover_url = serializers.SerializerMethodField()

    class Meta:
        model = Gallery
        fields = [
            'id',
            'title',
            'slug',
            'description',
            'cover_image',
            'cover_url',
            'photo_count',
        
            'is_featured',
            'created_at',
        ]

    def get_cover_url(self, obj):
        request = self.context.get('request')
        if obj.cover_image:
            return request.build_absolute_uri(obj.cover_image.url)
        return None

class GalleryDetailSerializer(serializers.ModelSerializer):
    # On imbrique les photos ici
    photos = PhotoSerializer(many=True, read_only=True)
    photo_count = serializers.IntegerField(read_only=True)
    cover_url = serializers.SerializerMethodField()

    class Meta:
        model = Gallery
        fields = [
            'id', 'title_fr', 'title_en', 'slug', 'description_fr', 'description_en',
            'cover_url', 'photo_count', 'is_featured', 'created_at', 'photos'
        ]

    def get_cover_url(self, obj):
        request = self.context.get('request')
        if obj.cover_image:
            return request.build_absolute_uri(obj.cover_image.url)
        return None

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
            "nom_fr",
            "nom_en",
            "date_debut",
            "date_fin",
            "mot_president_fr",
            "mot_president_en",
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

class ContactSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    subject = serializers.CharField(max_length=150)
    message = serializers.CharField()
    