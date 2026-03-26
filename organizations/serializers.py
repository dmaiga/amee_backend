from rest_framework import serializers
from organizations.models import Organization
from memberships.models import Membership
from roster.models import ConsultantProfile

class AboutSerializer(serializers.Serializer):
    organisations = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()

    def get_organisations(self, obj):
        orgs = Organization.objects.filter(est_actif=True)

        return [
            {
                "nom": org.nom,
                "sigle": org.sigle,
                "site_web": org.site_web,
                "email_contact": org.email_contact,
                "telephone": org.telephone,
                "siege": org.siege,
                "logo": org.logo.url if org.logo else None,
            }
            for org in orgs
        ]

    def get_stats(self, obj):
        return {
            "membres_actifs": Membership.objects.filter(
                statut="VALIDE"
            ).count(),
            "consultants_actifs": ConsultantProfile.objects.filter(
                statut="VALIDE",
            ).count(),
            "organisations_actifs": Organization.objects.filter(
                est_actif=True,
            ).count(),
        }