from rest_framework import serializers
from core.models import Dica, CategoriaDica


class DicaSerializer(serializers.ModelSerializer):
    categoria = serializers.PrimaryKeyRelatedField(queryset=CategoriaDica.objects.all())

    class Meta:
        model = Dica
        fields = ['id', 'titulo', 'resumo', 'conteudo', 'imagem', 'categoria', 'autor', 'publicada', 'data_publicacao']
    
        read_only_fields = ['autor'] 
