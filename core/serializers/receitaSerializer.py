from rest_framework import serializers
from core.models import Receita

class ReceitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receita
        fields = ['id', 'nome', 'descricao',  'tempo_preparo', 'rendimento', 'categoria', 'autor', 'imagem', 'disponivel']