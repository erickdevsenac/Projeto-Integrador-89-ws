from rest_framework import serializers

from core.models.carrinho import Carrinho, ItemCarrinho

from .pacote_surpresa_serializer import PacoteSurpresaSerializer
from .produto_serializer import ProdutoListSerializer


class ItemCarrinhoSerializer(serializers.ModelSerializer):
    produto_detalhes = ProdutoListSerializer(source="produto", read_only=True)
    pacote_detalhes = PacoteSurpresaSerializer(source="pacote", read_only=True)

    class Meta:
        model = ItemCarrinho
        fields = [
            "id",
            "quantidade",
            "subtotal",
            "produto",
            "pacote",
            "produto_detalhes",
            "pacote_detalhes",
        ]
        read_only_fields = ["subtotal"]


class CarrinhoSerializer(serializers.ModelSerializer):
    itens = ItemCarrinhoSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Carrinho
        fields = ["id", "usuario", "itens", "total"]

    def get_total(self, obj):
        return sum(item.subtotal for item in obj.itens.all())
