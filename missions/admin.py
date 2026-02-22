# missions/admin.py

from django.contrib import admin
from .models import Mission, MissionDocument

class MissionDocumentInline(admin.TabularInline):
    """Permet d'ajouter/modifier des documents directement dans la fiche Mission."""
    model = MissionDocument
    extra = 1  # Nombre de formulaires vides à afficher par défaut
    fields = ('nom', 'type_document', 'fichier', 'upload_par')

@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste
    list_display = (
        'titre', 
        'client', 
        'domaine', 
        'statut', 
        'budget_estime', 
        'cree_le'
    )
    
    # Filtres latéraux
    list_filter = ('statut', 'domaine', 'cree_le')
    
    # Barre de recherche
    search_fields = ('titre', 'client__email', 'client__last_name', 'domaine')
    
    # Organisation des champs dans le formulaire d'édition
    fieldsets = (
        ("Informations générales", {
            'fields': ('titre', 'client', 'expert_cible', 'statut')
        }),
        ("Détails de la mission", {
            'fields': ('description', 'objectifs', 'livrables_attendus', 'domaine')
        }),
        ("Paramètres logistiques", {
            'fields': ('localisation', 'duree_estimee_jours', 'budget_estime')
        }),
        ("Dates", {
            'fields': ('cree_le', 'publie_le'),
            'classes': ('collapse',), # Cache cette section par défaut
        }),
    )
    
    readonly_fields = ('cree_le',)
    inlines = [MissionDocumentInline]

@admin.register(MissionDocument)
class MissionDocumentAdmin(admin.ModelAdmin):
    list_display = ('nom', 'mission', 'type_document', 'cree_le', 'upload_par')
    list_filter = ('type_document', 'cree_le')
    search_fields = ('nom', 'mission__titre')