# /views/checkout.py

from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Prefetch
from django.core.paginator import Paginator
from core.models import Perfil, Pedido, PedidoVendedor, ItemPedido, Produto

@login_required(login_url="/login/")
@transaction.atomic
def finalizar_pedido(request):
    carrinho_session = request.session.get('carrinho', {})
    if not carrinho_session:
        messages.error(request, 'Seu carrinho está vazio.')
        return redirect('core:produtos')

    try:
        cliente_perfil = request.user.perfil
    except Perfil.DoesNotExist:
        messages.error(request, 'Perfil de cliente não encontrado.')
        return redirect('core:perfil')

    produto_ids = [int(pid) for pid in carrinho_session.keys()]
    produtos = {str(p.id): p for p in Produto.objects.select_for_update().filter(id__in=produto_ids)}
    
    total_pedido = Decimal('0.00')
    pedidos_por_vendedor = {}

    # Validação de estoque e agrupamento por vendedor
    for produto_id, item_data in carrinho_session.items():
        produto = produtos.get(produto_id)
        if not produto or item_data['quantidade'] > produto.quantidade_estoque:
            messages.error(request, f"Estoque insuficiente para '{produto.nome if produto else 'item desconhecido'}'.")
            return redirect('core:ver_carrinho')
        
        vendedor = produto.vendedor
        if vendedor not in pedidos_por_vendedor:
            pedidos_por_vendedor[vendedor] = {'itens': [], 'subtotal': Decimal('0.00')}
        
        subtotal_item = produto.preco * item_data['quantidade']
        pedidos_por_vendedor[vendedor]['itens'].append({'produto': produto, 'quantidade': item_data['quantidade'], 'preco_unitario': produto.preco})
        pedidos_por_vendedor[vendedor]['subtotal'] += subtotal_item
        total_pedido += subtotal_item

    if request.method == "POST":
        pedido_principal = Pedido.objects.create(cliente=cliente_perfil, valor_total=total_pedido)
        
        for vendedor, dados in pedidos_por_vendedor.items():
            sub_pedido = PedidoVendedor.objects.create(
                pedido_principal=pedido_principal,
                vendedor=vendedor,
                valor_subtotal=dados['subtotal']
            )
            for item in dados['itens']:
                produto_obj = item['produto']
                ItemPedido.objects.create(
                    sub_pedido=sub_pedido,
                    produto=produto_obj,
                    quantidade=item['quantidade'],
                    preco_unitario=item['preco_unitario']
                )
                produto_obj.quantidade_estoque -= item['quantidade']
                produto_obj.save()
        
        del request.session['carrinho']
        messages.success(request, f"Pedido #{pedido_principal.id} finalizado com sucesso!")
        return redirect('core:meus_pedidos')

    return render(request, 'core/checkout.html', {'carrinho': carrinho_session, 'total': total_pedido})


@login_required(login_url="/login/")
def meus_pedidos(request):
    try:
        perfil_usuario = request.user.perfil
    except Perfil.DoesNotExist:
        messages.error(request, "Seu perfil não foi encontrado.")
        return redirect("core:index")

    if perfil_usuario.tipo == Perfil.TipoUsuario.CLIENTE:
        pedidos_qs = Pedido.objects.filter(cliente=perfil_usuario).prefetch_related(
            Prefetch('sub_pedidos', queryset=PedidoVendedor.objects.select_related('vendedor')),
            Prefetch('sub_pedidos__itens', queryset=ItemPedido.objects.select_related('produto'))
        ).order_by('-data_pedido')
    elif perfil_usuario.tipo == Perfil.TipoUsuario.VENDEDOR:
       pedidos_qs = PedidoVendedor.objects.filter(vendedor=perfil_usuario).select_related(
            'pedido_principal__cliente'
        ).prefetch_related(
            Prefetch('itens', queryset=ItemPedido.objects.select_related('produto'))
        ).order_by('-pedido_principal__data_pedido')
    else:
        pedidos_qs = []
    
    paginator = Paginator(pedidos_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'tipo_usuario': perfil_usuario.tipo,
    }
    return render(request, 'core/meus_pedidos.html', context)