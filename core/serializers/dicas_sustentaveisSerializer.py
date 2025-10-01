from rest_framework import serializers
from core.models import Dica, CategoriaDica


class DicaSerializer(serializers.ModelSerializer):
    categoria = serializers.PrimaryKeyRelatedField(queryset=CategoriaDica.objects.all())

    class Meta:
        model = Dica
        fields = '__all__' 
    
        read_only_fields = ['autor'] 
        
class CategoriaDicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaDica
        fields = '__all__' 
