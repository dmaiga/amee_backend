from django.contrib import admin
from missions.models import Mission


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "titre",
        "client",
        "domaine",
        "statut",
        "duree_estimee_jours",
        "cree_le",
    )

    list_filter = (
        "statut",
        "domaine",
        "cree_le",
    )

    search_fields = (
        "titre",
        "client__email",
        "domaine",
    )

    readonly_fields = ("cree_le",)

    ordering = ("-cree_le",)
