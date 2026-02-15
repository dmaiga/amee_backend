from django.contrib import admin
from .models import Feedback, Signalement,IncidentReview
from django.utils.html import format_html



# =====================================================
# Action Admin
# =====================================================
@admin.action(description="Créer signalement niveau 1 (Surveillance)")
def signalement_niveau_1(modeladmin, request, queryset):
    for incident in queryset:
        if incident.statut != "CLOTURE":
            incident.creer_signalement(
                niveau=1,
                commentaire="Signalement suite enquête AMEE"
            )


@admin.action(description="Créer signalement niveau 2 (Suspension)")
def signalement_niveau_2(modeladmin, request, queryset):
    for incident in queryset:
        incident.creer_signalement(
            niveau=2,
            commentaire="Suspension décidée par AMEE"
        )

@admin.action(description="Passer en analyse")
def passer_en_analyse(modeladmin, request, queryset):
    queryset.update(statut="EN_ANALYSE")


# =====================================================
# Feedback Admin
# =====================================================

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "contact_request",
        "client",
        "get_consultant",
        "note",
        "cree_le",
    )

    list_filter = (
        "note",
        "cree_le",
    )

    search_fields = (
        "client__email",
        "contact_request__consultant__email",
        "contact_request__mission__titre",
    )

    readonly_fields = (
        "cree_le",
    )

    ordering = ("-cree_le",)

    def get_consultant(self, obj):
        return obj.contact_request.consultant
    get_consultant.short_description = "Consultant"


# =====================================================
# Signalement Admin
# =====================================================

@admin.register(Signalement)
class SignalementAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "consultant",
        "get_mission",
        "niveau",
        "cree_le",
    )

    list_filter = (
        "niveau",
        "cree_le",
    )

    search_fields = (
        "consultant__email",
        "incident__contact_request__mission__titre",
    )

    readonly_fields = ("cree_le",)

    ordering = ("-cree_le",)

    def get_mission(self, obj):
        return obj.incident.contact_request.mission.titre

    get_mission.short_description = "Mission"


# =====================================================
# IncidentReview Admin
# =====================================================

@admin.register(IncidentReview)
class IncidentReviewAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "get_mission",
        "consultant",
        "statut_consultant",
        "statut",
        "cree_le",
    )

    list_filter = (
        "statut",
        "cree_le",
    )

    search_fields = (
        "consultant__email",
        "contact_request__mission__titre",
        "contact_request__client__email",
    )

    readonly_fields = (
        "cree_le",
        "feedback",
        "contact_request",
        "consultant",
    )

    ordering = ("-cree_le",)
    actions = [
        passer_en_analyse,
        signalement_niveau_1,
        signalement_niveau_2,
    ]


    # 🔹 affichage mission plus lisible
    def get_mission(self, obj):
        return obj.contact_request.mission.titre

    get_mission.short_description = "Mission"

    def statut_consultant(self, obj):
        statut = obj.consultant.statut_qualite
    
        colors = {
            "NORMAL": "green",
            "SURVEILLANCE": "orange",
            "SUSPENDU": "red",
            "BANNI": "darkred",
        }
    
        return format_html(
            '<b style="color:{};">{}</b>',
            colors.get(statut, "black"),
            statut
        )
    
