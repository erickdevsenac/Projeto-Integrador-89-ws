from rest_framework import serializers
from ..models import Dica, CategoriaDica

class CategoriaDicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaDica
        fields = ['id', 'nome', 'slug']

class DicaSerializer(serializers.ModelSerializer):
    categoria = serializers.PrimaryKeyRelatedField(queryset=CategoriaDica.objects.all())

    class Meta:
        model = Dica
        fields = ['id', 'titulo', 'resumo', 'conteudo', 'imagem', 'categoria', 'autor', 'publicada', 'data_publicacao']
    
        read_only_fields = ['autor'] 
