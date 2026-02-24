from django.contrib import admin
from portals.models import ClientProfile


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):

    # -----------------------------
    # LISTE PRINCIPALE
    # -----------------------------
    list_display = (
        "nom_entreprise",
        "email_pro",
        "nom_contact",
        "statut_onboarding",
        "est_verifie",
        "user_active",
        "cree_le",
    )

    list_filter = (
        "statut_onboarding",
        "est_verifie",
        "cree_le",
    )

    search_fields = (
        "nom_entreprise",
        "email_pro",
        "nom_contact",
    )

    ordering = ("-cree_le",)

    readonly_fields = (
        "cree_le",
    )
    actions = ["valider_clients"]

    # -----------------------------
    # ORGANISATION FORMULAIRE
    # -----------------------------
    fieldsets = (

        ("Compte utilisateur", {
            "fields": ("user", "valide_par")
        }),

        ("Onboarding", {
            "fields": (
                "statut_onboarding",
                "est_verifie",
            )
        }),

        ("Entreprise", {
            "fields": (
                "nom_entreprise",
                "secteur_activite",
            )
        }),

        ("Contact", {
            "fields": (
                "nom_contact",
                "fonction_contact",
                "email_pro",
                "telephone_pro",
            )
        }),

        ("Audit", {
            "fields": ("cree_le",)
        }),
    )

    # -----------------------------
    # COLONNE ETAT USER
    # -----------------------------
    @admin.display(boolean=True, description="Compte actif")
    def user_active(self, obj):
        return obj.user.is_active
    
    
    @admin.action(description="Valider les clients sélectionnés")
    def valider_clients(self, request, queryset):
        for client in queryset:
            client.est_verifie = True
            client.statut_onboarding = "VALIDE"
            client.user.is_active = True
            client.user.save()
            client.save()