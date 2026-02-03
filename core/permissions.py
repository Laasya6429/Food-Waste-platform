from rest_framework.permissions import BasePermission


class IsDonor(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "DONOR"
        )


class IsNGO(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "NGO"
        )
