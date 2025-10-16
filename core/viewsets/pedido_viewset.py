from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import ItemPedido, Pedido, PedidoVendedor
from core.models.carrinho import Carrinho
from core.serializers import (  # Renomeado de pedido_serializer para PedidoListSerializer
    PedidoListSerializer,
    PedidoSerializer,
)


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Pedido.objects.filter(cliente=self.request.user.perfil)

    def get_serializer_class(self):
        if self.action == "list":
            return PedidoListSerializer  # Usando o nome correto do serializer
        return PedidoSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        cliente_perfil = request.user.perfil
        try:
            carrinho = cliente_perfil.carrinho
        except Carrinho.DoesNotExist:
            return Response(
                {"error": "Carrinho não encontrado ou vazio."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        itens_carrinho = carrinho.itens.all()
        if not itens_carrinho:
            return Response(
                {"error": "Carrinho vazio."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Adaptado da sua view 'finalizar_pedido'
        total_pedido = sum(item.subtotal for item in itens_carrinho)
        pedidos_por_vendedor = {}

        for item in itens_carrinho:
            item_obj = item.produto or item.pacote
            vendedor = item_obj.vendedor
            if vendedor not in pedidos_por_vendedor:
                pedidos_por_vendedor[vendedor] = {"itens": [], "subtotal": 0}

            pedidos_por_vendedor[vendedor]["itens"].append(item)
            pedidos_por_vendedor[vendedor]["subtotal"] += item.subtotal

        # Cria o Pedido principal
        pedido_principal = Pedido.objects.create(
            cliente=cliente_perfil,
            valor_produtos=total_pedido,
            endereco_entrega=request.data.get(
                "endereco_entrega", cliente_perfil.endereco
            ),
            forma_pagamento=request.data.get("forma_pagamento", "PIX"),
            # ... adicione lógica de cupom se necessário ...
        )

        for vendedor, dados in pedidos_por_vendedor.items():
            sub_pedido = PedidoVendedor.objects.create(
                pedido_principal=pedido_principal,
                vendedor=vendedor,
                valor_subtotal=dados["subtotal"],
            )
            for item_carrinho in dados["itens"]:
                item_obj = item_carrinho.produto or item_carrinho.pacote
                ItemPedido.objects.create(
                    sub_pedido=sub_pedido,
                    produto=item_carrinho.produto,
                    pacote_surpresa=item_carrinho.pacote,
                    quantidade=item_carrinho.quantidade,
                    preco_unitario=(item_obj.preco),
                )
                item_obj.quantidade_estoque -= item_carrinho.quantidade
                item_obj.save()

        # Limpa o carrinho
        carrinho.itens.all().delete()

        serializer = PedidoSerializer(pedido_principal)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
