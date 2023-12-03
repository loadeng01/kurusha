from rest_framework.permissions import BasePermission


class IsAuthorOrAdminOrEmployee(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        elif request.user.is_staff:
            return True
        return request.user == obj.owner


class IsAdminOrEmployee(BasePermission):
    # def has_object_permission(self, request, view, obj):
    #     if request.user.is_superuser:
    #         return True
    #     if request.user.is_staff:
    #         return True
    #     return False
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff or
                    request.user and request.user.is_superuser)


class IsActive(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_active


