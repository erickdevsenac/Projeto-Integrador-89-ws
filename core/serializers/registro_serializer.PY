from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import Perfil


class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    tipo_usuario = serializers.ChoiceField(
        choices=Perfil.TipoUsuario.choices, write_only=True
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
            "tipo_usuario",
        )
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            "email": {"required": True},
        }

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "As senhas não conferem."})
        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError({"email": "Este e-mail já está em uso."})
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )

        Perfil.objects.create(usuario=user, tipo=validated_data["tipo_usuario"])

        refresh = RefreshToken.for_user(user)
        return {
            "user": user,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, data):
        from django.contrib.auth import authenticate

        user = authenticate(username=data["username"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Credenciais inválidas")

        refresh = RefreshToken.for_user(user)
        data["user"] = user
        data["access"] = str(refresh.access_token)
        data["refresh"] = str(refresh)
        return data
