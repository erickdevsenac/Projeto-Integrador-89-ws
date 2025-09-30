# serializers.py
from rest_framework import serializers
from core.models.avaliacao_model import Avaliacao

class AvaliacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avaliacao
        fields = ['id', 'usuario', 'estrela', 'comentario', 'data_avaliacao']
        read_only_fields = ['usuario', 'data_avaliacao']
