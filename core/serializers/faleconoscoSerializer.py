from rest_framework import serializers
from  core.models.fale_conosco import FaleConosco
 
class FaleConoscoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaleConosco
        fields = '__all__'
        read_only_fields = ['data_envio']