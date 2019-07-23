from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets,mixins,generics, permissions,status,decorators
from app.models import User,Loan
from restapi import serializers 
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from django.contrib.auth import authenticate,login
from rest_framework.renderers import TemplateHTMLRenderer
from django.shortcuts import redirect



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

# USER INFORTMATIONS 

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated,]
    permission_classes_by_action = {'retrieve': [IsAuthenticated,IsOwnerOrReadOnly],
                                    'create':[IsOwnerOrReadOnly,permissions.IsAdminUser],
                                    'update':[IsOwnerOrReadOnly],
                                    'destroy':[IsOwnerOrReadOnly],
                                    }
    
    def get_permissions(self):
        try:
            # return permission_classes depending on `action` 
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError: 
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]


# AUTHENTICATIONS VIEWS 

class Login(mixins.CreateModelMixin, generics.GenericAPIView):

    serializer_class = serializers.UserLoginSerializer
   
    # Remove this during development
    def get(self,request):
        return Response()
    
    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        print(user)
        login(request,user)
        return Response(status=status.HTTP_202_ACCEPTED)



def GithubAuth(request):
    return redirect('github_login')

class VerifyYourself(generics.CreateAPIView):

    serializer_class = serializers.UserVerify
    permission_classes = [permissions.IsAuthenticated,]

    def get(self, request, *args, **kwargs):
        if not request.user.id_card:
            return Response('Verify Yourself')  
        return redirect('user-detail',request.user.id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.id_card = serializer.validated_data['idCard']
        if serializer.data['password']:
            request.user.set_password(serializer.validated_data['password'])
        request.user.save()
        headers = self.get_success_headers(serializer.data)
        return redirect('user-detail',request.user.id)


# User Functionalities



class Request(generics.CreateAPIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = serializers.RequestLoanSerializer
    '''
        REQUEST A RANGE OF MONEY FOR SPECIFIEC LENGTH
    '''
    def perform_create(self,serializer):
        serializer.receiver = self.request.user
        super().perform_create(serializer)




# SHOW ALL USER LOANS
class Accept(generics.RetrieveUpdateDestroyAPIView):
    '''
        ACCEPT OR DESTROY A LOAN
    '''
    permission_classes = [LoanOwner,IsAuthenticated]
    queryset = Loan.objects.filter(accepted=False)
    serializer_class = serializers.GiverLoanSerializer



    # THIS VIEW DISPLAY LOANS (ACCEPTED || WAITING) THAT WHERE REQUESTED TO THE CURRENT USER

@decorators.api_view(['GET',])
@decorators.permission_classes([IsAuthenticated])
def Loans(request,loan,loans_type):
    state = {'accepted':True,'waiting':False}
    if loan=='requested':
        serializer = serializers.RequestLoanSerializer(request.user.loan_receiver.filter(accepted=state[loans_type]),many=True,context={'request':request})
    else:
        serializer = serializers.GiverLoanSerializer(request.user.loan_giver.filter(accepted=state[loans_type]),many=True,context={'request':request})
    return Response(serializer.data)



