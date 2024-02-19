from rest_framework.permissions import IsAdminUser, SAFE_METHODS, BasePermission


class IsStaffOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or IsAdminUser().has_permission(request, view)


class IsAuthenticatedUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.user and
            request.user.is_authenticated
        )  # and (obj.user == request.user or request.user.is_staff)
