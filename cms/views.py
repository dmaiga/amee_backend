from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.shortcuts import get_object_or_404
from cms.models import Article, Resource, Opportunity,Photo,Mandat,Gallery


from cms.serializers import (
    ArticleSerializer,
    PublicResourceSerializer,
    PublicOpportunitySerializer,
    PhotoSerializer,
    MandatActifSerializer,
    ContactSerializer,
    GalleryListSerializer,
    GalleryDetailSerializer
)
from organizations.serializers import BureauSerializer
from rest_framework.views import APIView

# views.py
from rest_framework.response import Response
from django.views.decorators.cache import cache_page
from rest_framework import status, permissions
from django.core.mail import send_mail




# =====================================================
# ARTICLES (PUBLIC)
# =====================================================

class ArticleListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ArticleSerializer

    def get_queryset(self):
        return Article.objects.filter(publie=True).order_by("-date_publication")

class ArticleDetailView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = ArticleSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return Article.objects.filter(publie=True)

# --- RESOURCES ---
class PublicResourceListView(ListAPIView):
    serializer_class = PublicResourceSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Resource.objects.filter(reserve_aux_membres=False).order_by("-cree_le")

class PublicResourceDetailView(RetrieveAPIView):
    serializer_class = PublicResourceSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug_fr' # Ou 'id' selon votre préférence de routage

    def get_queryset(self):
        return Resource.objects.filter(reserve_aux_membres=False)


# --- OPPORTUNITIES ---
class PublicOpportunityListView(ListAPIView):
    serializer_class = PublicOpportunitySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Opportunity.objects.filter(
            publie=True, 
            reserve_aux_membres=False
        ).order_by("-cree_le")

class PublicOpportunityDetailView(RetrieveAPIView):
    serializer_class = PublicOpportunitySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug_fr'

    def get_queryset(self):
        return Opportunity.objects.filter(
            publie=True, 
            reserve_aux_membres=False
        )

class GalleryListAPIView(ListAPIView):
    queryset = Gallery.objects.all()
    serializer_class = GalleryListSerializer 
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()

        featured = self.request.query_params.get('featured')
        if featured:
            queryset = queryset.filter(is_featured=True)

        return queryset


class GalleryDetailAPIView(RetrieveAPIView):
    queryset = Gallery.objects.all()
    serializer_class = GalleryDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug' 

class PhotoListAPIView(ListAPIView):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()

        gallery_id = self.request.query_params.get('gallery')
        if gallery_id:
            queryset = queryset.filter(gallery_id=gallery_id)

        return queryset
    

# =====================================================
#
# =====================================================



class MandatActifAPIView(APIView):

    def get(self, request):
        mandat = Mandat.objects.filter(actif=True).first()

        if not mandat:
            return Response(
                {"detail": "Aucun mandat actif."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = MandatActifSerializer(mandat,context={"request": request})
        return Response(serializer.data)
    


class BureauAPIView(APIView):

    def get(self, request):
        serializer = BureauSerializer(instance={})
        return Response(serializer.data)
    

    # views.py






class ContactAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ContactSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data

            send_mail(
                subject=f"[AMEE Contact] {data['subject']}",
                message=f"""
Nom: {data['name']}
Email: {data['email']}

Message:
{data['message']}
""",
                from_email=None,
                recipient_list=["contact@amee-ml.com"],
                fail_silently=False,
            )

            return Response(
                {"message": "Message envoyé avec succès"},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)