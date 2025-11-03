from rest_framework.permissions import BasePermission


class IsSeller(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'seller'


class IsBuyer(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'buyer'


class IsSellerOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.seller == request.user