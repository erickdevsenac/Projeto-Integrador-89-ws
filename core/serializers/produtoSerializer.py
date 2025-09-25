from rest_framework import serializers
from core.models.produto_model import Produto
from rest_framework import serializers
class rodutoSerializer(serializers.ModelSerializer):
    class Meta :
        model = Produto
        fields =['categoria','vendedor','descricao','preco','imagem','data_fabricacao','data_validade']