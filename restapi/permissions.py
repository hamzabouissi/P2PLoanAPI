from rest_framework import permissions
from django.db.models import Q
from app.models import Loan

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.id_card == request.user.id_card

class LoanOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.giver == request.user  

    
class IsAuthenticated(permissions.BasePermission):
     def has_permission(self, request,view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        return request.user.is_authenticated and request.user.id_card is not None

class hasNoContraints(permissions.BasePermission):
     def has_permission(self, request,view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        return  not Loan.objects.filter(Q(giver=request.user)|Q(receiver=request.user)).exists()



class TrackOwer(permissions.BasePermission):

   def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.loan.giver == request.user and not obj.received