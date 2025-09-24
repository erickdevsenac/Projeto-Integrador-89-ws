from rest_framework import serializers
from ..models import Dica, CategoriaDica

class CategoriaDicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaDica
        fields = ['id', 'nome', 'slug']

    def validate_slug(self, value):
        """Validação para garantir que o slug seja único"""
        if CategoriaDica.objects.filter(slug=value).exists():
            raise serializers.ValidationError("Este slug já existe.")
        return value

class DicaSerializer(serializers.ModelSerializer):
    categoria = CategoriaDicaSerializer(read_only=True) 
    autor = serializers.StringRelatedField(read_only=True)  

    class Meta:
        model = Dica
        fields = ['id', 'titulo', 'resumo', 'conteudo', 'imagem', 'categoria', 'autor', 'publicada', 'data_publicacao']
    
    def validate(self, data):
        if len(data.get('titulo', '')) < 10:
            raise serializers.ValidationError("O título deve ter pelo menos 10 caracteres.")
        if len(data.get('resumo', '')) < 20:
            raise serializers.ValidationError("O resumo deve ter pelo menos 20 caracteres.")
        return data
