from django.contrib import admin
from .models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):

    list_display = ("nom", "email_contact", "est_actif")
    search_fields = ("nom", "sigle")
