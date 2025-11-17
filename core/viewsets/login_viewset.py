from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.serializers.registro_serializer import LoginSerializer, RegistroSerializer

class AuthViewSet(viewsets.GenericViewSet):
    queryset = None
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"], serializer_class=RegistroSerializer)
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_data = serializer.save()
        return Response(
            {"detail": "Cadastro realizado com sucesso. Verifique seu e-mail para ativar a conta."},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        
        if not user.is_active:
            return Response(
                {"detail": "Conta não ativada. Verifique seu e-mail."},
                status=status.HTTP_403_FORBIDDEN, 
            )
            
        return Response(
            {
                "user": user.username,
                "access": serializer.validated_data["access"],
                "refresh": serializer.validated_data["refresh"],
            },
            status=status.HTTP_200_OK,
        )
        
