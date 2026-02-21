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

