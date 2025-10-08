from decimal import Decimal
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from core.models import Produto

def ver_carrinho(request):
    """View otimizada para visualização do carrinho"""
    carrinho_session = request.session.get('carrinho', {})
    
    if not carrinho_session:
        return render(request, 'core/carrinho.html', {'carrinho': [], 'total_carrinho': Decimal('0.00')})
    
    produto_ids = [int(pid) for pid in carrinho_session.keys() if pid.isdigit()]
    produtos = {str(p.id): p for p in Produto.objects.filter(id__in=produto_ids)}
    
    carrinho_detalhado = []
    total_carrinho = Decimal('0.00')
    itens_removidos = []
    
    for produto_id, item_info in list(carrinho_session.items()):
        if produto_id not in produtos:
            itens_removidos.append(produto_id)
            continue
        
        produto = produtos[produto_id]
        quantidade = item_info['quantidade']
        
        if quantidade > produto.quantidade_estoque:
            item_info['quantidade'] = produto.quantidade_estoque
            quantidade = produto.quantidade_estoque
            if quantidade == 0:
                itens_removidos.append(produto_id)
                continue
        
        subtotal = produto.preco * quantidade
        total_carrinho += subtotal
        
        carrinho_detalhado.append({'produto': produto, 'quantidade': quantidade, 'subtotal': subtotal})
    
    if itens_removidos:
        for item_id in itens_removidos:
            del carrinho_session[item_id]
        request.session['carrinho'] = carrinho_session
        messages.warning(request, 'Alguns itens foram ajustados ou removidos do carrinho por falta de estoque.')
    
    return render(request, 'core/carrinho.html', {'carrinho': carrinho_detalhado, 'total_carrinho': total_carrinho})

@require_POST
def adicionar_carrinho(request, produto_id):
    """View para adicionar produtos ao carrinho"""
    produto = get_object_or_404(Produto, id=produto_id, ativo=True)
    carrinho = request.session.get('carrinho', {})
    
    try:
        quantidade_solicitada = int(request.POST.get("quantidade", 1))
        if quantidade_solicitada <= 0:
            raise ValueError
    except ValueError:
        messages.error(request, "Quantidade inválida.")
        return redirect(request.META.get("HTTP_REFERER", "core:produtos"))

    produto_id_str = str(produto.id)
    quantidade_existente = carrinho.get(produto_id_str, {}).get("quantidade", 0)
    
    if (quantidade_existente + quantidade_solicitada) > produto.quantidade_estoque:
        messages.error(request, f"Estoque insuficiente. Disponível: {produto.quantidade_estoque} unidades.")
        return redirect(request.META.get("HTTP_REFERER", "core:produtos"))

    carrinho[produto_id_str] = {
        'quantidade': quantidade_existente + quantidade_solicitada,
        'preco': str(produto.preco),
        'nome': produto.nome
    }
    
    request.session['carrinho'] = carrinho
    messages.success(request, f'{produto.nome} adicionado ao carrinho.')
    return redirect('core:ver_carrinho')

@require_POST
def atualizar_carrinho(request):
    """View para atualizar quantidades no carrinho via AJAX"""
    data = json.loads(request.body)
    produto_id = str(data.get('produto_id'))
    quantidade = int(data.get('quantidade', 0))
    
    carrinho = request.session.get('carrinho', {})
    
    if produto_id in carrinho:
        produto = get_object_or_404(Produto, id=int(produto_id))
        if quantidade > 0 and quantidade <= produto.quantidade_estoque:
            carrinho[produto_id]['quantidade'] = quantidade
        elif quantidade > produto.quantidade_estoque:
             return JsonResponse({'success': False, 'message': f'Estoque insuficiente ({produto.quantidade_estoque})'})
        else:
            del carrinho[produto_id]
        
        request.session['carrinho'] = carrinho
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'message': 'Produto não encontrado'})

@require_POST
def remover_item_carrinho(request, produto_id):
    """View para remover um item do carrinho"""
    carrinho = request.session.get('carrinho', {})
    produto_id_str = str(produto_id)
    
    if produto_id_str in carrinho:
        del carrinho[produto_id_str]
        request.session['carrinho'] = carrinho
        messages.success(request, "Item removido do carrinho.")
    
    return redirect("core:ver_carrinho")