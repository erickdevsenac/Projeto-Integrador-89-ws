from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from core.forms import ProdutoForm,CadastroPacoteSurpresa,PacoteSurpresaForm
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
            return redirect("core:index")
    else:
        form =CadastroPacoteSurpresa()
    return render(request, "core/pacote.html",context={"form":form})


def produtos(request):
  
    produtos = Produto.objects.select_related(
        "vendedor", "categoria"
    ).filter(
        ativo=True,
        quantidade_estoque__gt=0
    )

    pacotes = PacoteSurpresa.objects.filter(
        ativo=True,
        quantidade_estoque__gt=0
    )

    termo = request.GET.get("termo")
    if termo:
        produtos = produtos.filter(
            Q(nome__icontains=termo)
            | Q(descricao__icontains=termo)
            | Q(categoria__nome__icontains=termo)
            | Q(vendedor__nome_negocio__icontains=termo)
        ).distinct()

        pacotes = pacotes.filter(
            Q(nome__icontains=termo)
            | Q(descricao__icontains=termo)
        ).distinct()

   
    categoria_slug = request.GET.get("categoria")
    if categoria_slug:
        produtos = produtos.filter(categoria__slug=categoria_slug)

  
    preco_min = request.GET.get("preco_min")
    if preco_min:
        try:
            preco_min = Decimal(preco_min)
            produtos = produtos.filter(preco__gte=preco_min)
            pacotes = pacotes.filter(preco__gte=preco_min)
        except:
            pass

    preco_max = request.GET.get("preco_max")
    if preco_max:
        try:
            preco_max = Decimal(preco_max)
            produtos = produtos.filter(preco__lte=preco_max)
            pacotes = pacotes.filter(preco__lte=preco_max)
        except:
            pass
    ordenacao = request.GET.get("ordenacao", "-data_criacao")
    ordenacoes_validas = ["-data_criacao", "preco", "-preco", "nome"]
    if ordenacao in ordenacoes_validas:
        produtos = produtos.order_by(ordenacao)
        pacotes = pacotes.order_by(ordenacao)

 
    paginator = Paginator(produtos, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

 
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string(
            "core/_lista_produtos.html",
            {
                "page_obj": page_obj,
                "pacotes": pacotes,
                "request": request,
            },
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
        "pacotes": pacotes,
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

@login_required
def editar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)

    if produto.vendedor != request.user.perfil:
        messages.error(request, "Você não tem permissão para editar este produto.")
        return redirect("core:vendedor_perfil", usuario_id=request.user.id) 

    if request.method == "POST":
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'Produto "{produto.nome}" atualizado com sucesso!')
            
            return redirect("core:vendedor_perfil", usuario_id=produto.vendedor.usuario.id)
        
    else:
        
        form = ProdutoForm(instance=produto)

    
    return render(request, "core/editar_produto.html", {"form": form, "produto": produto})
@login_required
def excluir_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)

    try:
        vendedor_id = produto.vendedor.usuario.id
    except AttributeError:
        vendedor_id = request.user.id

    if produto.vendedor != request.user.perfil:
        messages.error(request, "Você não tem permissão para excluir este produto.")
        return redirect("core:vendedor_perfil", usuario_id=request.user.id) 

    if request.method == "POST":
        

        produto.delete()
        messages.success(request, f"Produto '{produto.nome}' excluído com sucesso!")
    
        return redirect("core:vendedor_perfil", usuario_id=vendedor_id)
    
    return redirect("core:vendedor_perfil", usuario_id=vendedor_id)

