from rest_framework import serializers
from organizations.models import Organization
from memberships.models import Membership
from roster.models import ConsultantProfile

class AboutSerializer(serializers.Serializer):

    organisation = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()

    def get_organisation(self, obj):
        org = Organization.objects.filter(est_actif=True).first()

        if not org:
            return None

        return {
            "nom": org.nom,
            "sigle": org.sigle,
            "site_web": org.site_web,
            "email_contact": org.email_contact,
            "telephone": org.telephone,
            "siege": org.siege,
            "logo": org.logo.url if org.logo else None,
        }

    def get_stats(self, obj):
        return {
            "membres_actifs": Membership.objects.filter(
                statut="VALIDE"
            ).count(),
            "consultants_actifs": ConsultantProfile.objects.filter(
                statut="VALIDE",
               
            ).count(),
        }