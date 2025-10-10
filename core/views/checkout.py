from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Prefetch
from django.core.paginator import Paginator

# Importe o formulário e os modelos necessários
from core.forms import CheckoutForm
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

    # --- 1. PREPARAÇÃO DOS DADOS (Válido para GET e POST) ---
    produto_ids = [int(pid) for pid in carrinho_session.keys()]
    produtos = {str(p.id): p for p in Produto.objects.select_for_update().filter(id__in=produto_ids)}
    
    carrinho_detalhado = []
    total_pedido = Decimal('0.00')
    pedidos_por_vendedor = {}

    # Loop único para processar o carrinho
    for produto_id, item_data in carrinho_session.items():
        produto = produtos.get(produto_id)
        quantidade = item_data['quantidade']

        # Validação de estoque feita no início
        if not produto or quantidade > produto.quantidade_estoque:
            messages.error(request, f"Estoque insuficiente para '{produto.nome if produto else 'item desconhecido'}'.")
            return redirect('core:ver_carrinho')

        subtotal = produto.preco * quantidade
        total_pedido += subtotal

        # Cria a lista de itens para o resumo no template
        carrinho_detalhado.append({
            'produto': produto,
            'quantidade': quantidade,
            'preco': produto.preco,
            'subtotal': subtotal,
            'nome': produto.nome,
        })
        
        # Agrupa itens por vendedor para a criação do pedido no POST
        vendedor = produto.vendedor
        if vendedor not in pedidos_por_vendedor:
            pedidos_por_vendedor[vendedor] = {'itens': [], 'subtotal': Decimal('0.00')}
        
        pedidos_por_vendedor[vendedor]['itens'].append({
            'produto': produto, 
            'quantidade': quantidade, 
            'preco_unitario': produto.preco
        })
        pedidos_por_vendedor[vendedor]['subtotal'] += subtotal

    # --- 2. LÓGICA DE PROCESSAMENTO (POST vs GET) ---
    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Cria o pedido principal
            pedido_principal = Pedido.objects.create(
                cliente=cliente_perfil,
                valor_produtos=total_pedido, # Usando o valor total dos produtos
                endereco_entrega=form.cleaned_data['endereco_entrega'],
                forma_pagamento=form.cleaned_data['forma_pagamento']
            )
            
            # Cria os sub-pedidos para cada vendedor
            for vendedor, dados in pedidos_por_vendedor.items():
                sub_pedido = PedidoVendedor.objects.create(
                    pedido_principal=pedido_principal,
                    vendedor=vendedor,
                    valor_subtotal=dados['subtotal']
                )
                # Adiciona os itens a cada sub-pedido e abate o estoque
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
            messages.success(request, f"Pedido #{pedido_principal.numero_pedido} finalizado com sucesso!")
            return redirect('core:meus_pedidos')
    else:
        # Para requisições GET, apenas cria o formulário com o endereço inicial
        form = CheckoutForm(initial={'endereco_entrega': cliente_perfil.endereco})

    # --- 3. CONTEXTO FINAL PARA O TEMPLATE ---
    context = {
        'form': form,
        'carrinho': carrinho_detalhado,
        'total_carrinho': total_pedido
    }
    
    return render(request, 'core/checkout.html', context)


@login_required(login_url="/login/")
def meus_pedidos(request):
    try:
        perfil_usuario = request.user.perfil
    except Perfil.DoesNotExist:
        messages.error(request, "Seu perfil não foi encontrado.")
        return redirect("core:index")

    if perfil_usuario.tipo == Perfil.TipoUsuario.CLIENTE:
        # CORREÇÃO: O campo de data é 'data_criacao', não 'data_pedido'
        pedidos_qs = Pedido.objects.filter(cliente=perfil_usuario).prefetch_related(
            Prefetch('sub_pedidos', queryset=PedidoVendedor.objects.select_related('vendedor')),
            Prefetch('sub_pedidos__itens', queryset=ItemPedido.objects.select_related('produto'))
        ).order_by('-data_criacao')
    elif perfil_usuario.tipo == Perfil.TipoUsuario.VENDEDOR:
        # CORREÇÃO: O campo de data é 'data_criacao', não 'data_pedido'
        pedidos_qs = PedidoVendedor.objects.filter(vendedor=perfil_usuario).select_related(
            'pedido_principal__cliente'
        ).prefetch_related(
            Prefetch('itens', queryset=ItemPedido.objects.select_related('produto'))
        ).order_by('-pedido_principal__data_criacao')
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