from rest_framework import viewsets
from core.serializers.loginSerializer import LoginSerializer
from django.contrib.auth.models import User

class LoginViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = LoginSerializer