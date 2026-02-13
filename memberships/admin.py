from django.contrib import admin

from memberships.models import Membership
 
@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'statut', 'est_actif', 'date_expiration')
    actions = ['valider_adhesion']

    @admin.action(description="Activer l'adhésion (Paiement reçu)")
    def valider_adhesion(self, request, queryset):
        for adhesion in queryset:
            adhesion.activer(valide_par=request.user)