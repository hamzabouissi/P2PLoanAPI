from rest_framework import serializers
from app.models import User,Loan
from datetime import datetime
from django.contrib.auth import authenticate
class UserSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = User
        fields = ['url','id_card','first_name','last_name','email','password','picture','money']
        read_only_fields = ['money','id_card','email']


class LoginSerializer(serializers.Serializer):

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


class GiverLoanSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Loan
        fields = ['url','accepted','receiver','length','amount']
        read_only_fields = ['receiver','length','amount','loaned_at']
    



class RequestLoanSerializer(serializers.HyperlinkedModelSerializer):
    
    receiver = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = Loan
        fields = ['url','giver','receiver','length','amount']
        read_only_fields = ['accepted','receiver']
    

class UserVerify(serializers.Serializer):
    idCard = serializers.IntegerField()


    def validate(self,data):
        if User.objects.filter(id_card=data['idCard']).exists():
            raise serializers.ValidationError('THIS ID CARD ALREADY EXISTS')
        return data

        