from rest_framework import permissions
from rest_framework.permissions import BasePermission

class EstMembreActifPourRessource(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Si la ressource n'est pas réservée, tout le monde voit
        if not obj.reserve_aux_membres:
            return True
        # Sinon, il faut être authentifié ET avoir une adhésion active
        return (
            request.user.is_authenticated and 
            hasattr(request.user, 'adhesion') and 
            request.user.adhesion.est_actif
        )

class EstMembreActif(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "adhesion")
            and request.user.adhesion.est_actif
        )

class EstBureauOuSuperAdmin(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and getattr(request.user, "role", None) in ["BUREAU", "SUPERADMIN"]
        )
    