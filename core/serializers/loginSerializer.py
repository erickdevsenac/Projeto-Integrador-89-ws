from rest_framework import serializers
from django.contrib.auth.models import User

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['password', 'email', 'username'] 
    