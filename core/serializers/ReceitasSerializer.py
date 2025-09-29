from rest_framework import serializers
from ..models import Receita
 
class ReceitasSerializer(serializers.ModelSerializer):
    class Meta:
        model= Receita
        fields= ['id', 'titulo', 'ingredientes', 'modo_preparo', 'tempo_preparo', 'porcoes']
 