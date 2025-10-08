from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    """Serializador para informações básicas do usuário."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']