# Em core/views.py

# --- Imports do Django ---
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from decimal import Decimal
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST


# --- Imports do Projeto ---
from .models import (
    Produto, Categoria, Perfil, Pedido, PedidoVendedor, ItemPedido, 
    Receita, Dica, EquipeDev
)
from .forms import (
    CadastroForm, ProdutoForm, ReceitaForm, IngredienteFormSet, 
    EtapaPreparoFormSet, PerfilForm
)

# --- Funções de Teste para Decorators ---
def is_vendedor(user):
    """Verifica se o usuário é um vendedor autenticado."""
    return user.is_authenticated and hasattr(user, 'perfil') and user.perfil.tipo == Perfil.TipoUsuario.VENDEDOR

# ==============================================================================
# VIEWS PÚBLICAS E INSTITUCIONAIS
# ==============================================================================

def index(request):
    return render(request, 'core/index.html')

def contato(request):
    return render(request, 'core/contato.html')

def devs(request):
    desenvolvedores = EquipeDev.objects.all()
    return render(request, 'core/timedev.html', {'equipe': desenvolvedores})

def doacao(request):
    ongs = Perfil.objects.filter(tipo="ONG")
    return render(request, 'core/doacao.html', {'instituicoes': ongs})

def videos(request):
    return render(request, 'core/videos.html')

# ==============================================================================
# VIEWS DE AUTENTICAÇÃO E PERFIL
# ==============================================================================

def cadastro(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(
                username=data['email'],
                email=data['email'],
                password=data['senha']
            )
            perfil = form.save(commit=False)
            perfil.usuario = user
            perfil.save()
            login(request, user)
            messages.success(request, f"Bem-vindo(a), {user.username}! Cadastro realizado com sucesso.")
            return redirect('core:index')
    else:
        form = CadastroForm()
    return render(request, "core/cadastro.html", {"form": form})

def login_view(request):
    mensagem = ""
    if request.method == "POST":
        email = request.POST.get("email")
        senha = request.POST.get("password")
        user = authenticate(request, username=email, password=senha)
        if user is not None:
            login(request, user)
            return redirect('core:index')
        else:
            mensagem = "Email ou senha incorretos."
    return render(request, "core/telalogin.html", {"mensagem": mensagem})

def logout_view(request):
    logout(request)
    return redirect('core:index')

@login_required(login_url='/login/')
def perfil(request):
    perfil = get_object_or_404(Perfil, usuario=request.user)
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado com sucesso!")
            return redirect('core:perfil')
    else:
        form = PerfilForm(instance=perfil)
    return render(request, 'core/perfil.html', {'form': form})

@login_required(login_url='/login/')
def configuracoes(request):
    # TODO: Implementar a lógica de configurações do usuário
    return render(request, 'core/configuracoes.html')

# TODO: Implementar a lógica de recuperação de senha (geralmente envolve envio de email)
def recuperarsenha(request):
    return render(request, 'core/recuperarsenha.html')

# TODO: Implementar a lógica de alteração de senha
def alterarsenha(request):
    return render(request, 'core/alterarsenha.html')

# ==============================================================================
# VIEWS DO MARKETPLACE (PRODUTOS, CARRINHO, CHECKOUT)
# ==============================================================================

def produtos(request):
    lista_produtos = Produto.objects.filter(ativo=True, quantidade_estoque__gt=0).order_by('-data_criacao')
    print(lista_produtos)
    categorias = Categoria.objects.all()
    
    categoria_slug = request.GET.get('categoria')
    if categoria_slug:
        lista_produtos = lista_produtos.filter(categoria__slug=categoria_slug)

    paginator = Paginator(lista_produtos, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    print(page_obj)

    context = {
        'page_obj': page_obj,
        'categorias': categorias,
        'categoria_atual': categoria_slug,
    }
    return render(request, 'core/produtos.html', context)

def buscar_produtos(request):
    termo = request.GET.get('termo', '')
    if termo:
        resultados = Produto.objects.filter(nome__icontains=termo)
    else:
        resultados = []
    return render(request, 'core/resultados_busca.html', {'resultados': resultados, 'termo': termo})

@user_passes_test(is_vendedor, login_url='/login/')
def cadastroproduto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            produto = form.save(commit=False)
            produto.vendedor = request.user.perfil
            produto.save()
            messages.success(request, f"Produto '{produto.nome}' cadastrado com sucesso!")
            return redirect('core:produtos')
    else:
        form = ProdutoForm()
    return render(request, 'core/cadastroproduto.html', {'form': form})

# --- Views do Carrinho ---

def ver_carrinho(request):
    carrinho_session = request.session.get('carrinho', {})
    carrinho_detalhado = []
    total_carrinho = Decimal('0.00')
    keys_para_remover = []

    for produto_id, item_info in carrinho_session.items():
        # AJUSTE: Adicionada verificação para ignorar chaves inválidas na sessão
        if not produto_id or not produto_id.isdigit():
            keys_para_remover.append(produto_id)
            continue

        preco_unitario = Decimal(item_info['preco'])
        quantidade = item_info['quantidade']
        subtotal = quantidade * preco_unitario
        carrinho_detalhado.append({
            'produto_id': produto_id, 'nome': item_info['nome'], 'quantidade': quantidade,
            'preco': preco_unitario, 'imagem_url': item_info.get('imagem_url', ''),
            'subtotal': subtotal, 'vendedor_nome': item_info.get('vendedor_nome', 'N/A'),
        })
        total_carrinho += subtotal
    
    # Limpa a sessão de quaisquer chaves inválidas encontradas
    if keys_para_remover:
        for key in keys_para_remover:
            del carrinho_session[key]
        request.session['carrinho'] = carrinho_session
        request.session.modified = True
        
    return render(request, 'core/carrinho.html', {'carrinho': carrinho_detalhado, 'total_carrinho': total_carrinho})

@require_POST
def adicionar_carrinho(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    carrinho = request.session.get('carrinho', {})
    quantidade_solicitada = int(request.POST.get('quantidade', 1))
    produto_id_str = str(produto.id)
    quantidade_no_carrinho = carrinho.get(produto_id_str, {}).get('quantidade', 0)
    quantidade_total_desejada = quantidade_no_carrinho + quantidade_solicitada

    if quantidade_total_desejada > produto.quantidade_estoque:
        messages.error(request, f"Desculpe, temos apenas {produto.quantidade_estoque} unidades de '{produto.nome}' em estoque.")
        return redirect(request.META.get('HTTP_REFERER', 'core:produtos'))

    if produto_id_str in carrinho:
        carrinho[produto_id_str]['quantidade'] = quantidade_total_desejada
    else:
        carrinho[produto_id_str] = {
            'quantidade': quantidade_total_desejada, 'preco': str(produto.preco),
            'nome': produto.nome, 'imagem_url': produto.imagem.url if produto.imagem else '',
            'vendedor_nome': produto.vendedor.nome_negocio,
        }
    request.session['carrinho'] = carrinho
    request.session.modified = True
    messages.success(request, f"'{produto.nome}' foi adicionado ao seu carrinho!")
    return redirect('core:ver_carrinho')

@require_POST
def atualizar_carrinho(request):
    # TODO: Implementar a lógica para atualizar a quantidade de múltiplos itens
    messages.info(request, "Funcionalidade de atualizar carrinho ainda não implementada.")
    return redirect('core:ver_carrinho')

def remover_item(request, produto_id):
    carrinho = request.session.get('carrinho', {})
    produto_id_str = str(produto_id)
    if produto_id_str in carrinho:
        del carrinho[produto_id_str]
        request.session['carrinho'] = carrinho
        request.session.modified = True
        messages.success(request, "Item removido do carrinho.")
    return redirect('core:ver_carrinho')

# --- Views de Pedidos ---

@login_required(login_url='/login/')
def finalizar_pedido(request):
    carrinho_session = request.session.get('carrinho', {})
    if not carrinho_session:
        messages.error(request, "Seu carrinho está vazio.")
        return redirect('core:produtos')

    carrinho_detalhado = []
    total_carrinho = Decimal('0.00')
    for produto_id, item_info in carrinho_session.items():
        subtotal = Decimal(item_info['preco']) * item_info['quantidade']
        total_carrinho += subtotal
        carrinho_detalhado.append({'produto_id': produto_id, 'quantidade': item_info['quantidade'], 'preco': Decimal(item_info['preco']), 'subtotal': subtotal})

    if request.method == 'POST':
        try:
            with transaction.atomic():
                cliente_perfil = request.user.perfil
                pedido = Pedido.objects.create(cliente=cliente_perfil, valor_total=total_carrinho, endereco_entrega=cliente_perfil.endereco)
                pedidos_por_vendedor = {}
                for item in carrinho_detalhado:
                    produto = Produto.objects.get(id=item['produto_id'])
                    vendedor_perfil = produto.vendedor
                    if vendedor_perfil not in pedidos_por_vendedor:
                        pedidos_por_vendedor[vendedor_perfil] = {'itens': [], 'subtotal': Decimal('0.00')}
                    pedidos_por_vendedor[vendedor_perfil]['itens'].append(item)
                    pedidos_por_vendedor[vendedor_perfil]['subtotal'] += item['subtotal']

                for vendedor, dados_pedido in pedidos_por_vendedor.items():
                    sub_pedido = PedidoVendedor.objects.create(pedido_principal=pedido, vendedor=vendedor, valor_subtotal=dados_pedido['subtotal'])
                    for item_data in dados_pedido['itens']:
                        produto = Produto.objects.get(id=item_data['produto_id'])
                        ItemPedido.objects.create(sub_pedido=sub_pedido, produto=produto, quantidade=item_data['quantidade'], preco_unitario=item_data['preco'])
                        produto.quantidade_estoque -= item_data['quantidade']
                        produto.save()
                del request.session['carrinho']
                messages.success(request, "Seu pedido foi finalizado com sucesso!")
                return redirect('core:meus_pedidos')
        except Exception as e:
            messages.error(request, f"Ocorreu um erro ao finalizar seu pedido: {e}")
            return redirect('core:ver_carrinho')

    return render(request, 'core/checkout.html', {'carrinho': carrinho_detalhado, 'total_carrinho': total_carrinho})

@login_required(login_url='/login/')
def meus_pedidos(request):
    try:
        perfil_usuario = request.user.perfil
    except Perfil.DoesNotExist:
        return render(request, 'core/meus_pedidos.html', {'pedidos': []})

    if perfil_usuario.tipo == Perfil.TipoUsuario.CLIENTE:
        pedidos = Pedido.objects.filter(cliente=perfil_usuario).order_by('-data_pedido')
        context = {'pedidos': pedidos, 'is_cliente': True}
    elif perfil_usuario.tipo == Perfil.TipoUsuario.VENDEDOR:
        pedidos = PedidoVendedor.objects.filter(vendedor=perfil_usuario).order_by('-id')
        context = {'pedidos': pedidos, 'is_cliente': False}
    else:
        context = {'pedidos': []}
    return render(request, 'core/meus_pedidos.html', context)

# ==============================================================================
# VIEWS DE CONTEÚDO (RECEITAS, DICAS)
# ==============================================================================

def receitas(request):
    lista_receitas = Receita.objects.filter(disponivel=True).order_by('-data_criacao')
    return render(request, 'core/receitas.html', {'receitas': lista_receitas})

def dicas(request):
    lista_dicas = Dica.objects.filter(publicada=True)
    return render(request, 'core/dicas.html', {'dicas': lista_dicas})

@login_required
def cria_receita(request):
    if request.method == 'POST':
        form = ReceitaForm(request.POST, request.FILES)
        ingrediente_formset = IngredienteFormSet(request.POST, prefix='ingredientes')
        etapa_formset = EtapaPreparoFormSet(request.POST, prefix='etapas')
        if form.is_valid() and ingrediente_formset.is_valid() and etapa_formset.is_valid():
            receita = form.save(commit=False)
            receita.autor = request.user
            receita.save()
            ingrediente_formset.instance = receita
            ingrediente_formset.save()
            etapa_formset.instance = receita
            etapa_formset.save()
            return redirect('core:receitas')
    else:
        form = ReceitaForm()
        ingrediente_formset = IngredienteFormSet(prefix='ingredientes')
        etapa_formset = EtapaPreparoFormSet(prefix='etapas')
    return render(request, 'core/cria_receita.html', {'form': form, 'ingrediente_formset': ingrediente_formset, 'etapa_formset': etapa_formset})
