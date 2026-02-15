from django.contrib import admin
from .models import Feedback, Signalement


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
        "niveau",
        "contact_request",
        "cree_le",
    )

    list_filter = (
        "niveau",
        "cree_le",
    )

    search_fields = (
        "consultant__email",
        "contact_request__mission__titre",
    )

    readonly_fields = (
        "cree_le",
    )

    ordering = ("-cree_le",)


