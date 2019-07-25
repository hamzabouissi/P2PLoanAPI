from rest_framework import serializers
from app.models import User,Loan,Track
from datetime import datetime
from django.contrib.auth import authenticate
class UserSerializer(serializers.HyperlinkedModelSerializer):

   
    class Meta:
        model = User
        fields = ['url','id_card','username','first_name','last_name','email','picture','money']
        read_only_fields = ['money','id_card','email']
        extra_kwargs = {
            "url":{'lookup_field':"id_card"}
        }


class UserLoginSerializer(serializers.Serializer):

    id_card = serializers.IntegerField()
    password = serializers.CharField(
        max_length=25,
        style={'input_type': 'password', 'placeholder': 'Password'}
        )
    def validate(self,data):
        user = authenticate(id_card=data['id_card'],password=data['password'])
        if user is None:
            raise serializers.ValidationError('Wrong Creedentials')
        return user

# LOAN SERIALIZERS
class LoanSerializer(serializers.HyperlinkedModelSerializer):
    tracks = serializers.HyperlinkedRelatedField(
            many=True,
            read_only=True,
            view_name='track-detail'
        )
    class Meta:
        model = Loan
        fields = ['giver','giver_acceptance','receiver','receiver_acceptance','length','amount','description','final_amount','loaned_at','tracks']
        extra_kwargs = {
                "receiver":{'lookup_field':"id_card"},
                "giver":{'lookup_field':"id_card"}
            
            }
        #read_only_fields = fields[:-1]

class GiverLoanSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Loan
        fields = ['url','giver_acceptance','receiver','length','amount','description','final_amount','receiver_acceptance']
        read_only_fields = ['receiver','length','description','receiver_acceptance']
        extra_kwargs = {
                "receiver":{'lookup_field':"id_card"}
            }
        
        
    def validate(self,data):
        giver = self.__dict__['_args'][0].giver
        if data['amount']>=giver.money:
            raise serializers.ValidationError('Current money not enough,recharge your account!')
        return data


class ReceiverAcceptanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['receiver_acceptance','giver','giver_acceptance','amount','final_amount','length']
        read_only_fields = ['giver','giver_acceptance','amount','final_amount','length']

class RequestLoanSerializer(serializers.HyperlinkedModelSerializer):
    
    receiver = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = Loan
        fields = ['url','giver','length','amount','description','receiver','final_amount']
        extra_kwargs = {
            "giver":{'lookup_field':"id_card"},
        }


class TrackSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Track
        fields = ['loan','expected_date','final_date','money','received']
        read_only_fields = ['loan','expected_date','final_date']

class UserVerify(serializers.Serializer):
    idCard = serializers.IntegerField(required=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self,data):
        if len(str(data['idCard']))!=8:
            raise serializers.ValidationError('INVALID ID CARD')
        if User.objects.filter(id_card=data['idCard']).exists():
            raise serializers.ValidationError('THIS ID CARD ALREADY EXISTS')
        return data

        
