from django.contrib import admin

from memberships.models import Membership
 
@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        
        'est_actif',
        'date_activation',
        'date_expiration',
    )

    readonly_fields = (
        'user',
        'date_activation',
        'date_expiration',
        'valide_par',
        'cree_le',
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
