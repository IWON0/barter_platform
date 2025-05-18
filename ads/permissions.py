from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user'):  # Ad
            return obj.user == request.user
        if hasattr(obj, 'ad_sender'):  # ExchangeProposal
            return obj.ad_sender.user == request.user
        return False
