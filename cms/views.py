from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from .models import Article, Resource, Opportunity
from .serializers import (
    ArticleSerializer,
    ResourceSerializer,
    OpportunitySerializer,
)
from .permissions import EstMembreActif


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


# =====================================================
# RESOURCES (MEMBRES UNIQUEMENT)
# =====================================================

class ResourceListView(ListAPIView):
    permission_classes = [EstMembreActif]
    serializer_class = ResourceSerializer

    def get_queryset(self):
        return Resource.objects.all().order_by("-cree_le")


class ResourceDetailView(RetrieveAPIView):
    permission_classes = [EstMembreActif]
    serializer_class = ResourceSerializer

    def get_queryset(self):
        return Resource.objects.all()


# =====================================================
# OPPORTUNITIES (MEMBRES PAR DEFAUT)
# =====================================================

class OpportunityListView(ListAPIView):
    permission_classes = [EstMembreActif]
    serializer_class = OpportunitySerializer

    def get_queryset(self):
        return Opportunity.objects.filter(publie=True).order_by("-cree_le")


class OpportunityDetailView(RetrieveAPIView):
    permission_classes = [EstMembreActif]
    serializer_class = OpportunitySerializer

    def get_queryset(self):
        return Opportunity.objects.filter(publie=True)
