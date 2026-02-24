from django.contrib import admin

from accounts.models import User
from django.contrib import admin, messages
from django.utils.crypto import get_random_string
from accounts.models import User

def desactiver_utilisateurs(modeladmin, request, queryset):
    queryset.update(is_active=False)

desactiver_utilisateurs.short_description = "🚫 Désactiver les comptes"

def reset_password(modeladmin, request, queryset):

    for user in queryset:
        new_password = "changeMe"
        
        user.set_password(new_password)
        user.save(update_fields=["password"])

        messages.success(
            request,
            f"{user.email} → nouveau mot de passe : {new_password}"
        )

reset_password.short_description = "🔑 Réinitialiser le mot de passe"


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = ('id','username','email','is_staff','is_active')
    list_filter = ('is_staff','is_active')
    search_fields = ('email','username')
    readonly_fields = ('id_membre_association',)

    actions = [reset_password, desactiver_utilisateurs]


