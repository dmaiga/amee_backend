from rest_framework.permissions import BasePermission

class IsCompta(BasePermission):

    def has_permission(self, request, view):
        return request.user.role == "COMPTA"

