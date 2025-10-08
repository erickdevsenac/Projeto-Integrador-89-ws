from rest_framework import serializers
from core.models.cupom import Cupom


class CupomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cupom
        fields = '__all__' 
        read_only_fields = ['usos_realizados']  
