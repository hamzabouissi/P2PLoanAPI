from rest_framework import serializers
from app.models import User,Loan,Track,Citizien,Notification
from datetime import datetime
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.conf import settings
import jwt

class CitizienSerializer(serializers.Serializer):

    last_name = serializers.CharField(max_length=25,required=False)
    id_card = serializers.IntegerField(required=False)


    

class UserRegistrationSerializer(serializers.ModelSerializer):

    password  = serializers.CharField(max_length=128, write_only=True, required=True)
    citizien =  CitizienSerializer(required=False)
    
    class Meta:
        model  = User
        fields = ['first_name','email','phone','location','picture','password','is_company','citizien']
        #read_only_fields  =['is_valid_profile']
    
    '''
    def validate_picture(self,picture):
            if not picture:
                raise serializers.ValidationError('You must include a Picture OF you')
            return picture
    '''
    
    def validate_password(self,password):
        return make_password(password)

    def create(self,validated_data):
        
        try:
            citizien = validated_data.pop('citizien')
        except KeyError:
            citizien = {}
        if len(citizien)!=2 and validated_data['is_company']==False:
            raise serializers.ValidationError('Complete the citizien informations')
        user = User.objects.create(**validated_data)
        if validated_data['is_company']==False:
            citizien['profile'] = user
            Citizien.objects.create(**citizien)
        return user
        

    
    


class UserSerializer(serializers.HyperlinkedModelSerializer):
    
    citizien =  CitizienSerializer(read_only=True)
    #notif = serializers.HyperlinkedRelatedField(many=True,read_only=True,view_name='notif-detail')

    class Meta:
        model = User
        fields = ['url','first_name','email','location','is_company','picture','money','password','citizien']
        read_only_fields = ['money','email','is_company']
        extra_kwargs ={
            'password':{'write_only':True}
        }
    
    def validate_password(self,password):
        return make_password(password)



class UserLoginSerializer(serializers.Serializer):

    email = serializers.CharField()
    password = serializers.CharField(
        max_length=25,
        style={'input_type': 'password', 'placeholder': 'Password'}
        )
    
    def validate(self,data):
        data = super().validate(data)
        user = authenticate(email=data['email'],password=data['password'])
        if user is not None:
            return user
        raise serializers.ValidationError('Wrong creedentials...')    
    
class PasswordChange(serializers.Serializer):

    password = serializers.CharField(max_length=25,required=True)
    password2 = serializers.CharField(max_length=25,required=True)
    token = serializers.CharField(max_length=300,required=True)

    def validate(self,data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError('password doesn\'t match')
        return data
    
    def save(self):
        token = self.validated_data['token']
        try:
            id = jwt.decode(token,settings.SECRET_KEY , algorithms=['HS256'])['user_id']
        except:
            raise serializers.ValidationError('INVALID TOKEN')
        user = User.objects.get(id=id)
        user.set_password(self.validated_data['password'])
        user.save()

# LOAN SERIALIZERS

class LoanSerializer(serializers.HyperlinkedModelSerializer):
    tracks = serializers.HyperlinkedRelatedField(
            many=True,
            read_only=True,
            view_name='track-detail',
        )

    class Meta:
        model = Loan
        fields = ['giver','giver_acceptance','receiver','receiver_acceptance','length','amount','description','loaned_at','tracks']
        extra_kwargs={
            "url":{'lookup_field':"uuid"}
        }   


class RequestLoanSerializer(serializers.HyperlinkedModelSerializer):
    
    
    class Meta:
        model = Loan
        fields = ['url','giver','length','amount','description','receiver','giver']
        extra_kwargs = {
            "url":{'lookup_field':"uuid"}
        }
    def validate(self,validated_data):
        user = self.context['request'].user
        giver = validated_data['giver']
        receiver = validated_data['receiver']

        if user not in [giver,receiver] or  [user]*2==[giver,receiver] : # Verify The Current User in request or he act as receiver and giver At the same time
            raise serializers.ValidationError('Dont fool Us')

        if user == giver:
            validated_data['giver_acceptance'] = True
        
        return validated_data




class TrackSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Track
        fields = ['loan','expected_date','final_date','money','received']
        read_only_fields = ['loan','expected_date','final_date']
        extra_kwargs = {
            "loan":{'lookup_field':"uuid"}
        }



class NotifSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields=['receiver','description','notification_type','creation_date','item']