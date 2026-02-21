from django.contrib import admin
from django.utils.html import format_html
from .models import Article, Resource, Opportunity


# =====================================================
# ARTICLE ADMIN (Actualités / Événements)
# =====================================================

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    fields = (
        "titre",
        "slug",
        "type",
        "contenu",
        "image",
        "publie",
        "date_publication",
        "lien_externe",
    )
    
    list_display = (
        "titre",
        "type",
        "statut_publication",
        "date_publication",
    )

    list_filter = (
        "type",
        "publie",
        "date_publication",
    )

    search_fields = ("titre", "contenu")

    prepopulated_fields = {"slug": ("titre",)}



    ordering = ("-date_publication",)

    def statut_publication(self, obj):
        if obj.publie:
            return format_html(
                '<b style="color:{};">{}</b>',
                "green",
                "Publié"
            )
        return format_html(
            '<b style="color:{};">{}</b>',
            "orange",
            "Brouillon"
        )

# =====================================================
# RESOURCE ADMIN (Bibliothèque membres)
# =====================================================

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):

    list_display = (
        "titre",
        "categorie",
        "reserve_aux_membres",
        "cree_le",
    )

    list_filter = (
        "categorie",
        "reserve_aux_membres",
    )

    search_fields = ("titre", "description")

    ordering = ("-cree_le",)


# =====================================================
# OPPORTUNITY ADMIN (Offres / Appels)
# =====================================================

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):

    list_display = (
        "titre",
        "type",
        "date_limite",
        "statut_expiration",
        "cree_le",
    )

    list_filter = (
        "type",
        "publie",
    )

    search_fields = ("titre", "description")

    ordering = ("-cree_le",)

    def statut_expiration(self, obj):
           if obj.est_expire:
               return format_html(
                   '<b style="color:{};">{}</b>',
                   "red",
                   "Expirée"
               )
           return format_html(
               '<b style="color:{};">{}</b>',
               "green",
               "Active"
           )
    statut_expiration.short_description = "Statut"

# =====================================================
# 
# =====================================================
