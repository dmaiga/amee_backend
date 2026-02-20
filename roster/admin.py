from django.contrib import admin
from roster.models import ConsultantProfile

@admin.register(ConsultantProfile)
class ConsultantProfileAdmin(admin.ModelAdmin):

    list_display = (
        "id",               
        "get_user_id",
        'user',
        'statut',
        'domaine_expertise',
        'annees_experience',
        'date_validation'
    )

    list_filter = ('statut',)

    actions = ['valider_candidature', 'rejeter_candidature']

    # -----------------------------
    # Affichage User ID
    # -----------------------------
    @admin.display(description="User ID")
    def get_user_id(self, obj):
        return obj.user.id

    @admin.action(description="Valider la candidature (BUREAU)")
    def valider_candidature(self, request, queryset):
        for profil in queryset:
            if profil.statut == 'SOUMIS':
                profil.valider(validateur=request.user)

    @admin.action(description="Rejeter la candidature")
    def rejeter_candidature(self, request, queryset):
        for profil in queryset:
            if profil.statut == 'SOUMIS':
                profil.refuser(validateur=request.user)
