from rest_framework.permissions import BasePermission


class EstBureauOuSuperAdmin(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['BUREAU', 'SUPERADMIN']
        )
