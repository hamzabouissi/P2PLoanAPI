from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets,mixins,generics, permissions,status,decorators,parsers
from app.models import User,Loan,Track,Citizien,Notification
from restapi import serializers 
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from django.contrib.auth import authenticate,login
from rest_framework.renderers import TemplateHTMLRenderer
from django.shortcuts import redirect
from restapi.permissions import IsOwnerOrReadOnly,LoanOwner,hasNoContraints,TrackOwner,ReadOnly
import jwt
from django.conf import settings
from django.core.mail import send_mail
from django_filters import rest_framework as filters
from django.db.models import Q



# USER INFORTMATIONS 

class UserViewSet(viewsets.ModelViewSet):

    '''
        SEE / UPDATE / DELETE YOUR PROFILE
        
    '''
    serializer_class = serializers.UserSerializer
    queryset = User.objects.all()
    permission_classes_by_action = {'retrieve': [ReadOnly],
                                    'create':[permissions.IsAdminUser],
                                    'update':[permissions.IsAuthenticated,IsOwnerOrReadOnly],
                                    'destroy':[permissions.IsAuthenticated,IsOwnerOrReadOnly,hasNoContraints ],
                                    'list':[ReadOnly,] # CHECK IF THE USER STILL HAD CONTAINTS BEFORE DELETION 
                                    }
    
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('location','citizien__id_card','is_company')
    
    # FILTER PERMISSION DEPEND ON HTTP METHOD
    def get_permissions(self):
        try:
            # return permission_classes depending on `action` 
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError: 
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]


# AUTHENTICATIONS VIEWS 
class Registration(generics.CreateAPIView):

    '''
        USER registration form
    '''
    parser_class = (parsers.FileUploadParser,parsers.JSONParser)
    serializer_class  = serializers.UserRegistrationSerializer
    queryset = User.objects.all()

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
        login(request,user)
        try:
            url = request.GET['next']
        except KeyError:
            return Response(status=status.HTTP_202_ACCEPTED)
        return redirect(url)


@decorators.api_view(['POST',])
def password_reset(request):
    email = request.data['email']
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist():
        return Response({'error':'invalid email'})
    encoded_jwt = jwt.encode({'user_id': user.id}, settings.SECRET_KEY, algorithm=settings.SIMPLE_JWT['ALGORITHM'])
    # Make it Async
    send_mail(
        'Password Reset',
        f'here is the link : http://p2ploan.taysircloud.com/api/password/reset/complete?token={encoded_jwt.decode()}',
        settings.EMAIL_HOST_USER,
        [email,]
    )
    return Response({'ok':'Link has been sent to your email'})


@decorators.api_view(['POST'])
def password_reset_complete(request):
    serializer = serializers.PasswordChange(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({'msg':'The user\'s password has been changed'})






# User Functionalities



class Request(generics.CreateAPIView):

    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = serializers.RequestLoanSerializer
    '''
        REQUEST A RANGE OF MONEY FOR SPECIFIEC LENGTH OR Send A Request to borrow 
    '''
    def perform_create(self,serializer):
        serializer.receiver = self.request.user
        super().perform_create(serializer)





class Accept(generics.RetrieveUpdateDestroyAPIView):
    '''
        ACCEPT OR DESTROY A LOAN
    '''
    permission_classes = [permissions.IsAuthenticated]
    queryset = Loan.objects.filter(receiver_acceptance=False) # PREVENT USER FROM ACCEPT TWICE THE SAME CONTRAINT
    serializer_class = serializers.GiverLoanSerializer
    lookup_field = 'uuid'

    '''
    def get_serializer_class(self):

        obj = self.get_object()

        if self.request.user == obj.receiver:
           
            serializer_class = serializers.ReceiverAcceptanceSerializer
        else:
            serializer_class = serializers.GiverLoanSerializer

        return serializer_class
    '''
    

class LoanDetail(generics.RetrieveAPIView):
    '''
        THIS VIEW SHOW THE HISRTORY OF CURRENT LOAN
    '''
    queryset = Loan.objects.all()
    serializer_class = serializers.LoanSerializer
    lookup_field = "uuid"



# THIS VIEW DISPLAY LOANS (ACCEPTED || WAITING) THAT WHERE REQUESTED TO THE CURRENT USER


class Loans(generics.ListAPIView):

    serializer_class = serializers.LoanSerializer
    permissions = [permissions.IsAuthenticated,]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('giver_acceptance','receiver_acceptance','receiver','giver')
    
    def get_queryset(self) :
        return Loan.objects.filter(Q(giver=self.request.user)| Q(receiver=self.request.user)).prefetch_related('tracks')

# PAYMENT 
class TrackDetail(generics.RetrieveUpdateAPIView):
    '''
        THIS VIEW TO TRACK LOAN HISTORY
    '''
    serializer_class = serializers.TrackSerializer
    queryset  = Track.objects.all()
    permission_classes = [TrackOwner,]
    lookup_field = 'pk'


class NotifList(generics.ListAPIView):
    '''
        THIS VIEW TO TRACK LOAN HISTORY
    '''
    serializer_class = serializers.NotifSerializer

    
    def get_queryset(self):
        return Notification.objects.filter(receiver=self.request.user)
        

class NotifDetail(generics.RetrieveAPIView):
    '''
        THIS VIEW TO TRACK LOAN HISTORY
    '''
    serializer_class = serializers.NotifSerializer
    queryset  = Notification.objects.all()
    #permission_classes = [TrackOwner,]
    lookup_field = 'pk'

def Page404(request,exception):
    return Response({'400':"We couldn't find Your search "},status=status.HTTP_400_BAD_REQUEST)

def Page500(request):
    
    return render(request,'error/500.htm')

