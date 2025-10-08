from rest_framework import serializers
from core.models.doacoes import Doacao

class DoacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doacao
        fields = '__all__'
        read_only_fields = ['id']
