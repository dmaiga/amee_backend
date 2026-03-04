from django.contrib import admin
from roster.models import ConsultantProfile

@admin.register(ConsultantProfile)
class ConsultantProfileAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "get_user_id",
        "user",
        "statut",
        "eligibilite_option",
        "annees_experience_ees",
        "est_disponible",
        "date_validation",
    )

    list_filter = (
        "statut",
        "eligibilite_option",
        "est_disponible",
    )
    search_fields = ("user__email", "user__id_membre_association")
    actions = ["valider_candidature", "rejeter_candidature"]

    # -----------------------------
    # Affichage User ID
    # -----------------------------
    @admin.display(description="User ID")
    def get_user_id(self, obj):
        return obj.user.id

    @admin.action(description="Valider la candidature (BUREAU)")
    def valider_candidature(self, request, queryset):
        for profil in queryset:
            if profil.statut == "SOUMIS":
                profil.valider(validateur=request.user)

    @admin.action(description="Rejeter la candidature")
    def rejeter_candidature(self, request, queryset):
        for profil in queryset:
            if profil.statut == "SOUMIS":
                profil.refuser(validateur=request.user)