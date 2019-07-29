from rest_framework import permissions
from django.db.models import Q
from app.models import Loan
from django.core.exceptions import ObjectDoesNotExist





class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.email == request.user.email

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
        return request.user.is_authenticated and request.user.is_valid_profile

class hasNoContraints(permissions.BasePermission):
     def has_permission(self, request,view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        return  not Loan.objects.filter(Q(giver=request.user)|Q(receiver=request.user)).exists()



class TrackOwner(permissions.BasePermission):

   def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.loan.giver == request.user and not obj.received