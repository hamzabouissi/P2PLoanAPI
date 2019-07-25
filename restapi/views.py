from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets,mixins,generics, permissions,status,decorators
from app.models import User,Loan,Track
from restapi import serializers 
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from django.contrib.auth import authenticate,login
from rest_framework.renderers import TemplateHTMLRenderer
from django.shortcuts import redirect
from restapi.permissions import IsOwnerOrReadOnly,IsAuthenticated,LoanOwner,hasNoContraints,TrackOwer




# USER INFORTMATIONS 

class UserViewSet(viewsets.ModelViewSet):

    '''
        SEE / UPDATE / DELETE YOUR PROFILE
        
    '''
    serializer_class = serializers.UserSerializer
    queryset = User.objects.all()
    lookup_field = 'id_card'
    permission_classes = [IsAuthenticated,]
    permission_classes_by_action = {'retrieve': [IsAuthenticated,IsOwnerOrReadOnly],
                                    'create':[IsOwnerOrReadOnly,permissions.IsAdminUser],
                                    'update':[IsOwnerOrReadOnly],
                                    'destroy':[IsOwnerOrReadOnly,hasNoContraints ] # CHECK IF THE USER STILL HAD CONTAINTS BEFORE DELETION 
                                    }
    
    # FILTER PERMISSION DEPEND ON HTTP METHOD
    def get_permissions(self):
        try:
            # return permission_classes depending on `action` 
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError: 
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]


# AUTHENTICATIONS VIEWS 

class Login(mixins.CreateModelMixin, generics.GenericAPIView):
    '''
        LOGIN FORM
    '''

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

    '''
        A FORM TO VERIFY USER'S IDENTITY 

    '''

    serializer_class = serializers.UserVerify
    permission_classes = [permissions.IsAuthenticated,]

    def get(self, request, *args, **kwargs):
        if not request.user.id_card:
            return Response('Verify Yourself')  
        # REDICRECT VERIFIED USER TO PROFILE PAGE
        return redirect('user-detail',request.user.id_card)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.id_card = serializer.validated_data['idCard']
        if serializer.data['password']:
            request.user.set_password(serializer.validated_data['password'])
        request.user.save()
        headers = self.get_success_headers(serializer.data)
        return redirect('user-detail',request.user.id_card)
    
   


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
    permission_classes = [IsAuthenticated]
    queryset = Loan.objects.filter(receiver_acceptance=False) # PREVENT USER FROM ACCEPT TWICE THE SAME CONTRAINT
    serializer_class = serializers.GiverLoanSerializer

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        obj = self.get_object()
        if self.request.user == obj.receiver:
           
            serializer_class = serializers.ReceiverAcceptanceSerializer
        else:
            serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)


class LoanDetail(generics.RetrieveAPIView):
    '''
        THIS VIEW SHOW THE HISRTORY OF CURRENT LOAN
    '''
    queryset = Loan.objects.all()
    serializer_class = serializers.LoanSerializer





# THIS VIEW DISPLAY LOANS (ACCEPTED || WAITING) THAT WHERE REQUESTED TO THE CURRENT USER

@decorators.api_view(['GET',])
@decorators.permission_classes([IsAuthenticated])
def Loans(request,loan,loans_type):
    '''
        SEE YOUR HISTORY
    '''
    state = {'accepted':True,'waiting':False}
    if loan=='requested':
        serializer = serializers.RequestLoanSerializer(request.user.loan_receiver.filter(giver_acceptance=state[loans_type]),many=True,context={'request':request})
    else:
        serializer = serializers.GiverLoanSerializer(request.user.loan_giver.filter(receiver_acceptance=state[loans_type],giver_acceptance=state[loans_type]),many=True,context={'request':request})
    return Response(serializer.data)




# TRACKS 
class TrackDetail(generics.RetrieveUpdateAPIView):
    '''
        THIS VIEW TO TRACK LOAN HISTORY
    '''
    serializer_class = serializers.TrackSerializer
    queryset  = Track.objects.all()
    permission_classes = [TrackOwer,]