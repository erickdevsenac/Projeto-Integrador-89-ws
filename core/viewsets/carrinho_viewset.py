from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models.carrinho import Carrinho, ItemCarrinho
from core.models.produto import PacoteSurpresa, Produto
from core.serializers.carrinho_serializer import CarrinhoSerializer


class CarrinhoViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CarrinhoSerializer

    def get_queryset(self):
        return Carrinho.objects.filter(usuario=self.request.user.perfil)

    def list(self, request, *args, **kwargs):
        carrinho, _ = Carrinho.objects.get_or_create(usuario=request.user.perfil)
        serializer = self.get_serializer(carrinho)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def adicionar_item(self, request):
        carrinho, _ = Carrinho.objects.get_or_create(usuario=request.user.perfil)
        produto_id = request.data.get("produto_id")
        pacote_id = request.data.get("pacote_id")
        quantidade = int(request.data.get("quantidade", 1))

        if not (produto_id or pacote_id):
            return Response(
                {"error": "ID do produto ou pacote é necessário."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item = None
        item_obj = None

        if produto_id:
            item_obj = Produto.objects.get(id=produto_id)
            item, created = ItemCarrinho.objects.get_or_create(
                carrinho=carrinho, produto=item_obj
            )
        elif pacote_id:
            item_obj = PacoteSurpresa.objects.get(id=pacote_id)
            item, created = ItemCarrinho.objects.get_or_create(
                carrinho=carrinho, pacote=item_obj
            )

        if not created:
            item.quantidade += quantidade
        else:
            item.quantidade = quantidade

        if item.quantidade > item_obj.quantidade_estoque:
            return Response(
                {"error": "Estoque insuficiente."}, status=status.HTTP_400_BAD_REQUEST
            )

        item.save()
        serializer = self.get_serializer(carrinho)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="remover-item")
    def remover_item(self, request, pk=None):
        # O pk aqui seria o ID do ItemCarrinho
        try:
            item = ItemCarrinho.objects.get(
                id=pk, carrinho__usuario=request.user.perfil
            )
            item.delete()
            carrinho = Carrinho.objects.get(usuario=request.user.perfil)
            serializer = self.get_serializer(carrinho)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ItemCarrinho.DoesNotExist:
            return Response(
                {"error": "Item não encontrado no carrinho."},
                status=status.HTTP_404_NOT_FOUND,
            )
