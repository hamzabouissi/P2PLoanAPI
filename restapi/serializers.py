from rest_framework import serializers
from app.models import User,Loan,Track,Citizien
from datetime import datetime
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password

class CitizienSerializer(serializers.Serializer):
    last_name = serializers.CharField(max_length=25,required=False)
    id_card = serializers.IntegerField(required=False)


    

class UserRegistrationSerializer(serializers.ModelSerializer):

    password  = serializers.CharField(max_length=128, write_only=True, required=True)
    citizien =  CitizienSerializer()
    
    class Meta:
        model  = User
        fields = ['first_name','email','phone','location','is_company','picture','password','is_valid_profile','citizien']
        read_only_fields  =['is_valid_profile']

    def validate_password(self,password):
        return make_password(password)
    
    def create(self,validated_data):
        citizien = validated_data.pop('citizien')
        if not citizien and validated_data['is_company']==False:
            raise serializers.ValidationError('User must Have Citizien caracteristics')
        user=User.objects.create(**validated_data)
        if validated_data['is_company']==False:
            citizien['profile'] =user
            print(citizien)
            Citizien.objects.create(**citizien)
        return user
        

    
    


class UserSerializer(serializers.HyperlinkedModelSerializer):
    
    citizien =  CitizienSerializer()
   
    class Meta:
        model = User
        fields = ['url','first_name','email','location','is_company','picture','money','citizien']
        read_only_fields = ['money','email','is_company']
        



class UserLoginSerializer(serializers.Serializer):

    email = serializers.CharField()
    password = serializers.CharField(
        max_length=25,
        style={'input_type': 'password', 'placeholder': 'Password'}
        )
    

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
        

class GiverLoanSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Loan
        fields = ['url','giver_acceptance','receiver','length','amount','description','final_amount','receiver_acceptance']
        read_only_fields = ['receiver','length','description','receiver_acceptance']
        
        
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



class TrackSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Track
        fields = ['loan','expected_date','final_date','money','received']
        read_only_fields = ['loan','expected_date','final_date']

class UserVerify(serializers.ModelSerializer):
    profile = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = Citizien
        fields = ['id_card','last_name','profile']

    def validate(self,data):
        if len(str(data['id_card']))!=8:
            raise serializers.ValidationError('INVALID ID CARD')
        if Citizien.objects.filter(id_card=data['id_card']).exists():
            raise serializers.ValidationError('THIS ID CARD ALREADY EXISTS')
        return data
    
