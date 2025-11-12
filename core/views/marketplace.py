from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string

# from django.views.decorators.cache import cache_page
from core.forms import ProdutoForm,CadastroPacoteSurpresa
from core.models import CategoriaProduto, Perfil, Produto, PacoteSurpresa

def pacote(request):
    queryset = PacoteSurpresa.objects.all().filter(
        ativo=True, quantidade_estoque__gt=0
    )
    if request.method == "POST":
        form = CadastroPacoteSurpresa(request.POST, request.FILES)
        if form.is_valid():
            pacote = form.save(commit=False)
            pacote.vendedor = request.user.perfil
            pacote.save()
            messages.success(
                request, f'Produto "{pacote.nome}" cadastrado com sucesso!'
            )
            return redirect("core:index.html")
    else:
        form =CadastroPacoteSurpresa()
    return render(request, "core/pacote.html",context={"form":form})


def produtos(request):
    """View otimizada para listagem de produtos e pacotes surpresa com filtros avançados"""
    queryset = Produto.objects.select_related("vendedor", "categoria").filter(
        ativo=True, quantidade_estoque__gt=0
    )

    pacotesurpresa = PacoteSurpresa.objects.filter(
        ativo=True, quantidade_estoque__gt=0
    )
    
    
    itens = list(queryset) + list(pacotesurpresa)
    print('itens:', itens)

    termo = request.GET.get("termo")
    if termo:
        queryset = queryset.filter(
            Q(nome__icontains=termo)
            | Q(descricao__icontains=termo)
            | Q(categoria__nome__icontains=termo)
            | Q(vendedor__nome_negocio__icontains=termo)
        ).distinct()

        pacotesurpresa = pacotesurpresa.filter(
            Q(nome__icontains=termo) | Q(descricao__icontains=termo)
        ).distinct()

    categoria_slug = request.GET.get("categoria")
    if categoria_slug:
        queryset = queryset.filter(categoria__slug=categoria_slug)

    preco_min = request.GET.get("preco_min")
    if preco_min:
        try:
            queryset = queryset.filter(preco__gte=Decimal(preco_min))
            pacotesurpresa = pacotesurpresa.filter(preco__gte=Decimal(preco_min))
        except (ValueError, TypeError):
            pass

    preco_max = request.GET.get("preco_max")
    if preco_max:
        try:
            queryset = queryset.filter(preco__lte=Decimal(preco_max))
            pacotesurpresa = pacotesurpresa.filter(preco__lte=Decimal(preco_max))
        except (ValueError, TypeError):
            pass

    ordenacao = request.GET.get("ordenacao", "-data_criacao")
    ordenacoes_validas = ["-data_criacao", "preco", "-preco", "nome"]
    if ordenacao in ordenacoes_validas:
        queryset = queryset.order_by(ordenacao)
        pacotesurpresa = pacotesurpresa.order_by(ordenacao)

    # ✅ junta as duas querysets em uma lista
    itens = list(queryset) + list(pacotesurpresa)

    # paginação
    paginator = Paginator(itens, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # AJAX
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string(
            "core/_lista_produtos.html", {"page_obj": page_obj, "request": request}
        )
        return JsonResponse({"html": html})

    categorias = CategoriaProduto.objects.annotate(
        produtos_count=Count(
            "produtos",
            filter=Q(produtos__ativo=True, produtos__quantidade_estoque__gt=0),
        )
    ).filter(produtos_count__gt=0)

    context = {
        "page_obj": page_obj,
        # "pacotes_produtos": query_mesclada,
        "categorias": categorias,
        "categoria_atual": categoria_slug,
        "filtros": {
            "preco_min": preco_min,
            "preco_max": preco_max,
            "ordenacao": ordenacao,
        },
    }

    return render(request, "core/produtos.html", context)



def buscar_produtos(request):
    """View para busca de produtos com múltiplos critérios"""
    termo = request.GET.get("termo", "").strip()

    if not termo:
        return render(
            request, "core/resultados_busca.html", {"resultados": [], "termo": termo}
        )

    resultados = (
        Produto.objects.select_related("vendedor", "categoria")
        .filter(
            Q(nome__icontains=termo)
            | Q(descricao__icontains=termo)
            | Q(categoria__nome__icontains=termo)
            | Q(vendedor__nome_negocio__icontains=termo),
            ativo=True,
            quantidade_estoque__gt=0,
        )
        .distinct()
        .order_by("-data_criacao")
    )

    paginator = Paginator(resultados, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "termo": termo,
        "total_resultados": paginator.count,
    }
    return render(request, "core/resultados_busca.html", context)


def produto_detalhe(request, produto_id):
    """View para exibir detalhes de um produto específico"""
    produto = get_object_or_404(
        Produto.objects.select_related("vendedor", "categoria"),
        id=produto_id,
        ativo=True,
    )

    produtos_relacionados = Produto.objects.filter(
        categoria=produto.categoria, ativo=True, quantidade_estoque__gt=0
    ).exclude(id=produto.id)[:4]

    content_type = ContentType.objects.get_for_model(Produto)

    avaliacoes = produto.avaliacoes.all().order_by("-data_criacao")
    context = {
        "produto": produto,
        "produtos_relacionados": produtos_relacionados,
        "content_type_id": content_type.id,
        "avaliacoes": avaliacoes,
    }
    return render(request, "core/produto_detalhe.html", context)


def produto_quick_view(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    html = render_to_string("core/_quick_view_content.html", {"produto": produto})
    return JsonResponse({"html": html})


@login_required(login_url="/login/")
def cadastrar_produto(request):
    if request.user.perfil.tipo != Perfil.TipoUsuario.VENDEDOR:
        messages.error(request, "Apenas vendedores podem cadastrar produtos.")
        return redirect("core:index")

    if request.method == "POST":
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            produto = form.save(commit=False)
            produto.vendedor = request.user.perfil
            produto.save()
            messages.success(
                request, f'Produto "{produto.nome}" cadastrado com sucesso!'
            )
            return redirect("core:produtos")
    else:
        form = ProdutoForm()

    return render(request, "core/cadastroproduto.html", {"form": form})
