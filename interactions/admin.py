from django.contrib import admin
from .models import ContactRequest


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "mission",
        "client",
        "consultant",
        "statut",
        "est_collaboration_validee",
        "date_suivi_prevu",
        "suivi_effectue",
        "cree_le",
    )

    list_filter = (
        "statut",
        "suivi_effectue",
        "est_collaboration_validee",
        "cree_le",
    )

    search_fields = (
        "client__email",
        "consultant__email",
        "mission__titre",
    )

    readonly_fields = (
        "cree_le",
        "est_collaboration_validee",
    )

    ordering = ("-cree_le",)

from django.utils import timezone


@admin.action(description="Marquer le suivi comme effectué")
def marquer_suivi(modeladmin, request, queryset):
    queryset.update(
        suivi_effectue=True,
        date_suivi_reel=timezone.now()
    )
