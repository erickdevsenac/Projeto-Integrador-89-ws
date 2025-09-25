from rest_framework import serializers
from core.models import Cupom

class CupomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cupom
        fields = ['PERCENTUAL', 'VALOR_FIXO']
