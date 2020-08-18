from rest_framework.permissions import BasePermission

class IsEditorUser(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser or request.user.has_perm("meituan.change_merchant"):
            return True
        else:
            return False

class IsFinanceUser(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser or request.user.has_perm("meituan.change_order"):
            return True
        else:
            return False