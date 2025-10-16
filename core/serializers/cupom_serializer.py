from rest_framework import serializers
from core.models.cupom import Cupom


class CupomSerializer(serializers.ModelSerializer):
    """Serializador para Cupom de Produto."""
    
    class Meta:
        model = Cupom
        fields = '__all__' 
        read_only_fields = ['usos_realizados']  
