from rest_framework import serializers
from core.models.produto_model import Produto

class ProdutoSerializer(serializers.ModelSerializer):
    class Meta :
        model = Produto
        fields =['categoria','vendedor','descricao','preco','imagem','data_fabricacao','data_validade']