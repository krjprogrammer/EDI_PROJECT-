# serializers.py
from rest_framework import serializers
from .models import files, Archive
from django.contrib.auth.models import User
import re


# Serializer for user signup (creating a new user)
class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}
        
    def validate_username(self, value):
        # Ensure the username only contains letters
        if not re.match(r'^[a-zA-Z]+$', value):
            raise serializers.ValidationError("Username should only contain letters.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

# Serializer for login (using Django's built-in authentication)
class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100)
    
class OTPLoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=100, required=True)  
    otp = serializers.CharField(max_length=6, required=True)    
    

class FilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = files
        fields = '__all__'
        
class ArchiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Archive
        fields = '__all__'        
