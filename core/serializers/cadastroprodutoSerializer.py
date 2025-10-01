from rest_framework import serializers
from core.models.cadastroprodutos_model import Cadastro_Produto

class CadastroProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cadastro_Produto
        fields = '__all__'
      