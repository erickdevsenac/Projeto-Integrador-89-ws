from rest_framework import viewsets
from core.serializers.login_serializer import LoginSerializer
from django.contrib.auth.models import User

class LoginViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = LoginSerializer