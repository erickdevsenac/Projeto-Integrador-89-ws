from rest_framework import serializers
from core.models.dicas_sustentaveis import Dica, CategoriaDica



class CategoriaDicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaDica
        fields = '__all__'

class DicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dica
        fields = '__all__'
        read_only_fields = ['autor']