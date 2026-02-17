from django.contrib import admin
from django.utils.html import format_html
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):

    # ===============================
    # LIST DISPLAY
    # ===============================
    list_display = (
        "id",
        "affichage_payeur",
        "categorie",
        "type_transaction",
        "montant",
        "statut_badge",
        "date_transaction",
        "cree_par",
    )

    list_filter = (
        "statut",
        "categorie",
        "type_transaction",
        "date_transaction",
    )

    search_fields = (
        "membre__email",
        "email_payeur",
        "description",
    )

    ordering = ("-cree_le",)

    # ===============================
    # AFFICHAGE PAYEUR INTELLIGENT
    # ===============================
    def affichage_payeur(self, obj):
        if obj.membre:
            return f"{obj.membre.email} ({obj.membre.id_membre_association})"
        return obj.email_payeur or "-"
    affichage_payeur.short_description = "Payeur"

    # ===============================
    # BADGE STATUT
    # ===============================
    def statut_badge(self, obj):

        colors = {
            "BROUILLON": "orange",
            "VALIDEE": "green",
            "ANNULEE": "red",
        }

        return format_html(
            '<b style="color:{};">{}</b>',
            colors.get(obj.statut, "black"),
            obj.get_statut_display()
        )

    statut_badge.short_description = "Statut"

    # ===============================
    # ACTIONS COMPTABLES
    # ===============================
    @admin.action(description="✅ Valider les transactions")
    def valider_transactions(self, request, queryset):
        for transaction in queryset:
            if transaction.statut == "BROUILLON":
                transaction.statut = "VALIDEE"
                transaction.save()

    @admin.action(description="❌ Annuler les transactions")
    def annuler_transactions(self, request, queryset):
        queryset.update(statut="ANNULEE")

    actions = [
        "valider_transactions",
        "annuler_transactions",
    ]

    # ===============================
    # LOCK APRÈS VALIDATION
    # ===============================
    def get_readonly_fields(self, request, obj=None):

        if obj and obj.statut == "VALIDEE":
            return (
                "statut",
                "type_transaction",
                "categorie",
                "montant",
                "membre",
                "email_payeur",
                "date_transaction",
                "description",
                "cree_par",
            )

        return ()

    # ===============================
    # AUTO CREATEUR
    # ===============================
    def save_model(self, request, obj, form, change):
        if not obj.cree_par:
            obj.cree_par = request.user
        super().save_model(request, obj, form, change)
