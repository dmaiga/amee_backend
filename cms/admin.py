from django.contrib import admin
from django.utils.html import format_html
from .models import Article, Resource, Opportunity

from django.utils.html import format_html

# =====================================================
# ARTICLE ADMIN (Actualités / Événements)
# =====================================================
from modeltranslation.admin import TranslationAdmin 
from django.utils.html import format_html

@admin.register(Article)
class ArticleAdmin(TranslationAdmin):
    
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

 

    def statut_publication(self, obj):
        if obj.publie:
            # On passe "Publié" en argument pour satisfaire format_html
            return format_html(
                '<b style="color:green;">{}</b>', 
                "Publié"
            )
        return format_html(
            '<b style="color:orange;">{}</b>', 
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
from django.contrib import admin
from cms.models import BoardMembership,BoardRole,Mandat

# Register your models here.
@admin.register(BoardRole)
class BoardRoleAdmin(admin.ModelAdmin):
    list_display = ("titre", "ordre", "actif")
    list_editable = ("ordre", "actif")

@admin.register(Mandat)
class MandatAdmin(admin.ModelAdmin):
    list_display = ("nom", "date_debut", "date_fin", "actif")

@admin.register(BoardMembership)
class BoardMembershipAdmin(admin.ModelAdmin):
    list_display = ("membership", "mandat", "role")   