from rest_framework import serializers
from core.models import notificacao_model

class NotificacaoSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = notificacao_model
        fields = [
            'id', 
            'tipo', 
            'tipo_display', 
            'titulo', 
            'mensagem', 
            'url_destino', 
            'lida', 
            'data_criacao'
        ]
        read_only_fields = ['usuario', 'data_criacao']