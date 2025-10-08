from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.views.decorators.cache import cache_page

from core.models import Produto, CategoriaProduto

@cache_page(60 * 5)  # Cache de 5 minutos
def produtos(request):
    """View otimizada para listagem de produtos com filtros avançados"""
    queryset = Produto.objects.select_related('vendedor', 'categoria').filter(
        ativo=True, 
        quantidade_estoque__gt=0
    )
    
    # Filtros
    categoria_slug = request.GET.get('categoria')
    if categoria_slug:
        queryset = queryset.filter(categoria__slug=categoria_slug)
    
    preco_min = request.GET.get('preco_min')
    if preco_min:
        try:
            queryset = queryset.filter(preco__gte=Decimal(preco_min))
        except (ValueError, TypeError):
            pass
    
    preco_max = request.GET.get('preco_max')
    if preco_max:
        try:
            queryset = queryset.filter(preco__lte=Decimal(preco_max))
        except (ValueError, TypeError):
            pass
    
    # Ordenação
    ordenacao = request.GET.get('ordenacao', '-data_criacao')
    ordenacoes_validas = ['-data_criacao', 'preco', '-preco', 'nome']
    if ordenacao in ordenacoes_validas:
        queryset = queryset.order_by(ordenacao)
    
    # Paginação
    paginator = Paginator(queryset, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Categorias com contagem de produtos
    categorias = CategoriaProduto.objects.annotate(
        produtos_count=Count('produtos', filter=Q(produtos__ativo=True, produtos__quantidade_estoque__gt=0))
    ).filter(produtos_count__gt=0)
    
    context = {
        'page_obj': page_obj,
        'categorias': categorias,
        'categoria_atual': categoria_slug,
        'filtros': {
            'preco_min': preco_min,
            'preco_max': preco_max,
            'ordenacao': ordenacao,
        }
    }
    return render(request, 'core/produtos.html', context)


def buscar_produtos(request):
    """View para busca de produtos com múltiplos critérios"""
    termo = request.GET.get('termo', '').strip()
    
    if not termo:
        return render(request, 'core/resultados_busca.html', {'resultados': [], 'termo': termo})
    
    resultados = Produto.objects.select_related('vendedor', 'categoria').filter(
        Q(nome__icontains=termo) | 
        Q(descricao__icontains=termo) |
        Q(categoria__nome__icontains=termo) |
        Q(vendedor__nome_negocio__icontains=termo),
        ativo=True,
        quantidade_estoque__gt=0
    ).distinct().order_by('-data_criacao')
    
    paginator = Paginator(resultados, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'termo': termo,
        'total_resultados': paginator.count
    }
    return render(request, 'core/resultados_busca.html', context)


def produto_detalhe(request, produto_id):
    """View para exibir detalhes de um produto específico"""
    produto = get_object_or_404(
        Produto.objects.select_related('vendedor', 'categoria'),
        id=produto_id,
        ativo=True
    )
    
    produtos_relacionados = Produto.objects.filter(
        categoria=produto.categoria,
        ativo=True,
        quantidade_estoque__gt=0
    ).exclude(id=produto.id)[:4]
    
    context = {
        'produto': produto,
        'produtos_relacionados': produtos_relacionados,
    }
    return render(request, 'core/produto_detalhe.html', context)