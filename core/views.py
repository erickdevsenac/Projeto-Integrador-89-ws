from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Prefetch, Count, F
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core.cache import cache
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.http import JsonResponse
from django.utils import timezone

import json

from core.models import Cupom

from .forms import (
    CadastroForm,
    CupomForm,
    EtapaPreparoFormSet,
    IngredienteFormSet,
    PerfilForm,
    ReceitaForm,
)

# --- Imports do Projeto ---
from .models import (
    Categoria,
    Dica,
    EquipeDev,
    ItemPedido,
    Pedido,
    PedidoVendedor,
    Perfil,
    Produto,
    Receita,
)


# --- Funções de Teste para Decorators ---
def is_vendedor(user):
    """Verifica se o usuário é um vendedor autenticado."""
    return (
        user.is_authenticated
        and hasattr(user, "perfil")
        and user.perfil.tipo == Perfil.TipoUsuario.VENDEDOR
    )


# ==============================================================================
# VIEWS PÚBLICAS E INSTITUCIONAIS
# ==============================================================================


def index(request):
    return render(request, 'core/index.html')

def ongs_pagina(request, usuario_id):
    ongs_pagina = get_object_or_404(Perfil, tipo = "ONG", usuario_id = usuario_id)
    context = {
        "inf_ongs": ongs_pagina
    }
    return render(request, 'core/ong_pagina.html', context)

def produtos(request):
    lista_produtos = Produto.objects.filter(ativo=True, quantidade_estoque__gt=0).order_by('-data_criacao')
    
    paginator = Paginator(lista_produtos, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/produtos.html', {'page_obj': page_obj})

def contato(request):
    return render(request, "core/contato.html")


def devs(request):
    desenvolvedores = EquipeDev.objects.all()
    return render(request, "core/timedev.html", {"equipe": desenvolvedores})


def doacao(request):
    ongs = Perfil.objects.filter(tipo="ONG")
    return render(request, "core/doacao.html", {"instituicoes": ongs})


def videos(request):
    return render(request, "core/videos.html")


# ==============================================================================
# VIEWS DE AUTENTICAÇÃO E PERFIL
# ==============================================================================


def cadastro(request):
    if request.method == "POST":
        form = CadastroForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(
                username=data["email"], email=data["email"], password=data["senha"]
            )
            perfil = form.save(commit=False)
            perfil.usuario = user
            perfil.save()
            login(request, user)
            messages.success(
                request,
                f"Bem-vindo(a), {user.username}! Cadastro realizado com sucesso.",
            )
            return redirect("core:index")
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
            return redirect("core:index")
        else:
            mensagem = "Email ou senha incorretos."
    return render(request, "core/telalogin.html", {"mensagem": mensagem})


def logout_view(request):
    logout(request)
    return redirect("core:index")


@login_required(login_url="/login/")
def perfil(request):
    perfil = get_object_or_404(Perfil, usuario=request.user)
    if request.method == "POST":
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado com sucesso!")
            return redirect("core:perfil")
    else:
        form = PerfilForm(instance=perfil)
    return render(request, "core/perfil.html", {"form": form})


@login_required(login_url="/login/")
def configuracoes(request):
    if request.method == 'POST':
        # Checa a lógica de exclusão primeiro
        if 'excluir_conta' in request.POST:
            # Lógica para deletar a conta do usuário
            request.user.delete()
            return redirect('core:index')

        # Se não for uma exclusão, processa as outras configurações
        tema = request.POST.get('tema')
        fonte = request.POST.get('fonte')
        acessibilidade = request.POST.get('acessibilidade')
        notificacoes = request.POST.get('notificacoes')

        if tema:
            request.session['theme'] = tema
        if fonte:
            request.session['fonte'] = fonte
        if acessibilidade: 
            request.session['acessibilidade'] = acessibilidade
        if notificacoes:
            request.session['notificacoes'] = notificacoes
        
        return redirect('core:configuracoes')

    # Lógica GET para apenas renderizar a página
    return render(request, "core/configuracoes.html")


# TODO: Implementar a lógica de recuperação de senha (geralmente envolve envio de email)
def recuperarsenha(request):
    if request.method == 'POST':
        email_do_usuario = request.POST.get('email')
    
        try:
            usuario = User.objects.get(email=email_do_usuario)
        except User.DoesNotExist:
            messages.error(request, 'Não há conta associada a este e-mail.')
            return render(request, 'recuperarsenha.html')
            
        # Cria o token de recuperação de senha
        uid = urlsafe_base64_encode(force_bytes(usuario.pk))
        token = default_token_generator.make_token(usuario)
        
        # Cria o link de redefinição
        link_de_reset = request.build_absolute_uri(
            f'/redefinir-senha/{uid}/{token}/' # Substitua pela sua URL real
        )
        
        # Cria o corpo do e-mail com o link de reset
        corpo_email = render_to_string('email/senha_reset.html', {
            'usuario': usuario,
            'link_de_reset': link_de_reset,
        })
        
        try:
            send_mail(
                'Redefinição de Senha',
                corpo_email,
                'seu_email@exemplo.com', 
                [usuario.email],
                fail_silently=False,
            )
            messages.success(request, 'Um e-mail com instruções foi enviado.')
            return redirect('core:telalogin') # Redireciona para uma página de sucesso
        except Exception as e:
            messages.error(request, f'Ocorreu um erro ao enviar o e-mail: {e}')
    return render(request, "core/recuperarsenha.html")


# TODO: Implementar a lógica de alteração de senha
def alterarsenha(request):
    return render(request, "core/alterarsenha.html")


# ==============================================================================
# VIEWS DO MARKETPLACE (PRODUTOS, CARRINHO, CHECKOUT)
# ==============================================================================
@cache_page(60 * 5)  # Cache por 5 minutos
def produtos(request):
    """View otimizada para listagem de produtos com filtros avançados"""
    # Query otimizada com select_related e prefetch_related
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
    
    # Paginação otimizada
    paginator = Paginator(queryset, 12)  # Aumentado para 12 produtos
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Categorias com contagem de produtos
    categorias = Categoria.objects.annotate(
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
    """View melhorada para busca de produtos com múltiplos critérios"""
    termo = request.GET.get('termo', '').strip()
    
    if not termo:
        return render(request, 'core/resultados_busca.html', {
            'resultados': [],
            'termo': termo,
            'total_resultados': 0
        })
    
    # Busca otimizada em múltiplos campos
    resultados = Produto.objects.select_related('vendedor', 'categoria').filter(
        Q(nome__icontains=termo) | 
        Q(descricao__icontains=termo) |
        Q(categoria__nome__icontains=termo) |
        Q(vendedor__nome_negocio__icontains=termo),
        ativo=True,
        quantidade_estoque__gt=0
    ).distinct().order_by('-data_criacao')
    
    # Paginação
    paginator = Paginator(resultados, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'resultados': page_obj,  # Para compatibilidade com template existente
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
    
    # Produtos relacionados da mesma categoria
    produtos_relacionados = Produto.objects.select_related('vendedor').filter(
        categoria=produto.categoria,
        ativo=True,
        quantidade_estoque__gt=0
    ).exclude(id=produto.id)[:4]
    
    context = {
        'produto': produto,
        'produtos_relacionados': produtos_relacionados,
    }
    return render(request, 'core/produto_detalhe.html', context)

# ==============================================================================
# VIEWS DO CARRINHO
# ==============================================================================

def ver_carrinho(request):
    """View otimizada para visualização do carrinho"""
    carrinho_session = request.session.get('carrinho', {})
    
    if not carrinho_session:
        return render(request, 'core/carrinho.html', {
            'carrinho': [],
            'total_carrinho': Decimal('0.00'),
            'quantidade_total': 0
        })
    
    # Buscar produtos em uma única query
    produto_ids = [int(pid) for pid in carrinho_session.keys() if pid.isdigit()]
    produtos = {
        str(p.id): p for p in Produto.objects.select_related('vendedor').filter(
            id__in=produto_ids,
            ativo=True
        )
    }
    
    carrinho_detalhado = []
    total_carrinho = Decimal('0.00')
    quantidade_total = 0
    itens_removidos = []
    
    for produto_id, item_info in carrinho_session.items():
        if produto_id not in produtos:
            itens_removidos.append(produto_id)
            continue
        
        produto = produtos[produto_id]
        quantidade = item_info['quantidade']
        
        # Verificar se há estoque suficiente
        if quantidade > produto.quantidade_estoque:
            quantidade = produto.quantidade_estoque
            carrinho_session[produto_id]['quantidade'] = quantidade
            if quantidade == 0:
                itens_removidos.append(produto_id)
                continue
        
        subtotal = produto.preco * quantidade
        total_carrinho += subtotal
        quantidade_total += quantidade
        
        carrinho_detalhado.append({
            'produto': produto,
            'quantidade': quantidade,
            'subtotal': subtotal,
        })
    
    # Remover itens inválidos
    for item_id in itens_removidos:
        del carrinho_session[item_id]
    
    if itens_removidos:
        request.session['carrinho'] = carrinho_session
        request.session.modified = True
        messages.warning(request, 'Alguns itens foram removidos do carrinho por falta de estoque.')
    
    context = {
        'carrinho': carrinho_detalhado,
        'total_carrinho': total_carrinho,
        'quantidade_total': quantidade_total,
    }
    return render(request, 'core/carrinho.html', context)


@require_POST
def adicionar_carrinho(request, produto_id):
    """View otimizada para adicionar produtos ao carrinho"""
    produto = get_object_or_404(Produto, id=produto_id, ativo=True)
    
    if produto.quantidade_estoque <= 0:
        messages.error(request, 'Produto fora de estoque.')
        return redirect('core:produtos')
    
    quantidade = int(request.POST.get('quantidade', 1))
    if quantidade <= 0:
        messages.error(request, 'Quantidade inválida.')
        return redirect('core:produtos')
    
    carrinho = request.session.get('carrinho', {})
    produto_id_str = str(produto_id)
    
    if produto_id_str in carrinho:
        nova_quantidade = carrinho[produto_id_str]['quantidade'] + quantidade
    else:
        nova_quantidade = quantidade
    
    # Verificar estoque disponível
    if nova_quantidade > produto.quantidade_estoque:
        messages.error(request, f'Estoque insuficiente. Disponível: {produto.quantidade_estoque} unidades.')
        return redirect('core:produtos')
    
    carrinho[produto_id_str] = {
        'nome': produto.nome,
        'preco': str(produto.preco),
        'quantidade': nova_quantidade,
        'imagem': produto.imagem.url if produto.imagem else None,
    }
    
    request.session['carrinho'] = carrinho
    request.session.modified = True
    
    messages.success(request, f'{produto.nome} adicionado ao carrinho.')
    return redirect('core:produtos')


@require_POST
def atualizar_carrinho(request):
    """View para atualizar quantidades no carrinho via AJAX"""
    if request.content_type == 'application/json':
        data = json.loads(request.body)
        produto_id = str(data.get('produto_id'))
        quantidade = int(data.get('quantidade', 0))
    else:
        produto_id = str(request.POST.get('produto_id'))
        quantidade = int(request.POST.get('quantidade', 0))
    
    carrinho = request.session.get('carrinho', {})
    
    if produto_id not in carrinho:
        return JsonResponse({'success': False, 'message': 'Produto não encontrado no carrinho.'})
    
    if quantidade <= 0:
        del carrinho[produto_id]
        message = 'Item removido do carrinho.'
    else:
        # Verificar estoque
        produto = get_object_or_404(Produto, id=int(produto_id))
        if quantidade > produto.quantidade_estoque:
            return JsonResponse({
                'success': False, 
                'message': f'Estoque insuficiente. Disponível: {produto.quantidade_estoque} unidades.'
            })
        
        carrinho[produto_id]['quantidade'] = quantidade
        message = 'Carrinho atualizado.'
    
    request.session['carrinho'] = carrinho
    request.session.modified = True
    
    # Calcular novo total
    total = Decimal('0.00')
    for item in carrinho.values():
        total += Decimal(item['preco']) * item['quantidade']
    
    return JsonResponse({
        'success': True,
        'message': message,
        'total_carrinho': str(total),
        'quantidade_itens': sum(item['quantidade'] for item in carrinho.values())
    })


@require_POST
def remover_item_carrinho(request, produto_id):
    """View para remover item do carrinho"""
    carrinho = request.session.get('carrinho', {})
    produto_id_str = str(produto_id)
    
    if produto_id_str in carrinho:
        nome_produto = carrinho[produto_id_str]['nome']
        del carrinho[produto_id_str]
        request.session['carrinho'] = carrinho
        request.session.modified = True
        messages.success(request, f'{nome_produto} removido do carrinho.')
    
    return redirect('core:ver_carrinho')


# --- Views de Pedidos ---

# ==============================================================================
# VIEWS DE CHECKOUT
# ==============================================================================
@login_required(login_url="/login/")
@transaction.atomic
def finalizar_pedido(request):
    carrinho_session = request.session.get('carrinho', {})
    
    if not carrinho_session:
        messages.error(request, 'Seu carrinho está vazio.')
        return redirect('core:produtos')
    
    # Verificar se o usuário tem perfil de cliente
    try:
        cliente_perfil = request.user.perfil
        if cliente_perfil.tipo != Perfil.TipoUsuario.CLIENTE:
            messages.error(request, 'Apenas clientes podem fazer pedidos.')
            return redirect('core:produtos')
    except Perfil.DoesNotExist:
        messages.error(request, 'Perfil não encontrado. Complete seu cadastro.')
        return redirect('core:perfil')
    
    # Buscar produtos e validar estoque
    produto_ids = [int(pid) for pid in carrinho_session.keys() if pid.isdigit()]
    produtos = {
        str(p.id): p for p in Produto.objects.select_related('vendedor').filter(
            id__in=produto_ids,
            ativo=True
        )
    }
    
    carrinho_detalhado = []
    total_carrinho = Decimal('0.00')
    erros_estoque = []
    
    for produto_id, item_info in carrinho_session.items():
        if produto_id not in produtos:
            continue
        
        produto = produtos[produto_id]
        quantidade = item_info['quantidade']
        
        if quantidade > produto.quantidade_estoque:
            erros_estoque.append(f'{produto.nome}: estoque insuficiente (disponível: {produto.quantidade_estoque})')
            continue
        
        subtotal = produto.preco * quantidade
        total_carrinho += subtotal
        
        carrinho_detalhado.append({
            'produto': produto,
            'quantidade': quantidade,
            'preco': produto.preco,
            'subtotal': subtotal,
        })
    
    if erros_estoque:
        for erro in erros_estoque:
            messages.error(request, erro)
        return redirect('core:ver_carrinho')
    
    if not carrinho_detalhado:
        messages.error(request, 'Nenhum produto válido no carrinho.')
        return redirect('core:produtos')
    
    if request.method == 'POST':
        forma_pagamento = request.POST.get('forma_pagamento', 'PIX')
        endereco_entrega = request.POST.get('endereco_entrega', cliente_perfil.endereco)
        
        if not endereco_entrega:
            messages.error(request, 'Endereço de entrega é obrigatório.')
            return render(request, 'core/checkout.html', {
                'carrinho': carrinho_detalhado,
                'total_carrinho': total_carrinho,
                'cliente': cliente_perfil,
            })
        
        try:
            # Criar pedido principal
            pedido = Pedido.objects.create(
                cliente=cliente_perfil,
                valor_total=total_carrinho,
                endereco_entrega=endereco_entrega,
                forma_pagamento=forma_pagamento,
            )
            
            # Agrupar itens por vendedor
            pedidos_por_vendedor = {}
            for item in carrinho_detalhado:
                vendedor = item['produto'].vendedor
                if vendedor not in pedidos_por_vendedor:
                    pedidos_por_vendedor[vendedor] = {
                        'itens': [],
                        'subtotal': Decimal('0.00'),
                    }
                pedidos_por_vendedor[vendedor]['itens'].append(item)
                pedidos_por_vendedor[vendedor]['subtotal'] += item['subtotal']
            
            # Criar sub-pedidos e itens
            for vendedor, dados_pedido in pedidos_por_vendedor.items():
                sub_pedido = PedidoVendedor.objects.create(
                    pedido_principal=pedido,
                    vendedor=vendedor,
                    valor_subtotal=dados_pedido['subtotal'],
                )
                
                for item_data in dados_pedido['itens']:
                    produto = item_data['produto']
                    quantidade = item_data['quantidade']
                    
                    # Verificar estoque novamente (double-check)
                    if quantidade > produto.quantidade_estoque:
                        raise ValueError(f'Estoque insuficiente para {produto.nome}')
                    
                    ItemPedido.objects.create(
                        sub_pedido=sub_pedido,
                        produto=produto,
                        quantidade=quantidade,
                        preco_unitario=item_data['preco'],
                    )
                    
                    # Atualizar estoque
                    produto.quantidade_estoque -= quantidade
                    produto.save(update_fields=['quantidade_estoque'])
            
            # Limpar carrinho
            del request.session['carrinho']
            request.session.modified = True
            
            messages.success(request, f'Pedido #{pedido.id} finalizado com sucesso!')
            return redirect('core:meus_pedidos')
            
        except Exception as e:
            messages.error(request, f'Erro ao finalizar pedido: {str(e)}')
            return redirect('core:ver_carrinho')
    
    context = {
        'carrinho': carrinho_detalhado,
        'total_carrinho': total_carrinho,
        'cliente': cliente_perfil,
        'formas_pagamento': Pedido.FormaPagamento.choices,
    }
    return render(request, 'core/checkout.html', context)


@login_required(login_url="/login/")
def meus_pedidos(request):
    try:
        perfil_usuario = request.user.perfil
    except Perfil.DoesNotExist:
        return render(request, "core/meus_pedidos.html", {"pedidos": []})

    if perfil_usuario.tipo == Perfil.TipoUsuario.CLIENTE:
        pedidos = Pedido.objects.filter(cliente=perfil_usuario).prefetch_related(
            Prefetch('sub_pedidos', queryset=PedidoVendedor.objects.select_related('vendedor')),
            Prefetch('sub_pedidos__itens', queryset=ItemPedido.objects.select_related('produto'))
        ).order_by('-data_pedido')
    elif perfil_usuario.tipo == Perfil.TipoUsuario.VENDEDOR:
       pedidos = PedidoVendedor.objects.filter(vendedor=perfil_usuario).select_related(
            'pedido_principal', 'pedido_principal__cliente'
        ).prefetch_related(
            Prefetch('itens', queryset=ItemPedido.objects.select_related('produto'))
        ).order_by('-pedido_principal__data_pedido')
    else:
        pedidos = []
    
    paginator = Paginator(pedidos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'pedidos': page_obj, 
        'tipo_usuario': perfil_usuario.tipo,
    }
    return render(request, 'core/meus_pedidos.html', context)


# ==============================================================================
# VIEWS DE CONTEÚDO (RECEITAS, DICAS)
# ==============================================================================


def receitas(request):
    # AJUSTE: Adicionada paginação para a lista de receitas
    lista_receitas = Receita.objects.filter(disponivel=True).order_by('-data_criacao')
    
    paginator = Paginator(lista_receitas, 9) # Exibe 9 receitas por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/receitas.html', {'page_obj': page_obj})

def receita_detalhe(request, receita_id):
    """
    Exibe os detalhes completos de uma única receita.
    """
    receita = get_object_or_404(Receita, id=receita_id, disponivel=True)
    return render(request, 'core/receita_detalhe.html', {'receita': receita})

def dicas(request):
    lista_dicas = Dica.objects.filter(publicada=True)
    return render(request, "core/dicas.html", {"dicas": lista_dicas})


@login_required
def cria_receita(request):
    if request.method == "POST":
        form = ReceitaForm(request.POST, request.FILES)
        ingrediente_formset = IngredienteFormSet(request.POST, prefix="ingredientes")
        etapa_formset = EtapaPreparoFormSet(request.POST, prefix="etapas")
        if (
            form.is_valid()
            and ingrediente_formset.is_valid()
            and etapa_formset.is_valid()
        ):
            receita = form.save(commit=False)
            receita.autor = request.user
            receita.save()
            ingrediente_formset.instance = receita
            ingrediente_formset.save()
            etapa_formset.instance = receita
            etapa_formset.save()
            return redirect("core:receitas")
    else:
        form = ReceitaForm()
        ingrediente_formset = IngredienteFormSet(prefix="ingredientes")
        etapa_formset = EtapaPreparoFormSet(prefix="etapas")
    return render(
        request,
        "core/cria_receita.html",
        {
            "form": form,
            "ingrediente_formset": ingrediente_formset,
            "etapa_formset": etapa_formset,
        },
    )


# Função para garantir que apenas administradores acessem
def is_admin(user):
    return user.is_staff


@user_passes_test(is_admin)
def criar_cupom(request):
    if request.method == "POST":
        form = CupomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cupom criado com sucesso!")
            return redirect("core:index")

    else:
        form = CupomForm()

    return render(request, "core/cupom.html", {"form": form})

def debug_email_test(request):
    return HttpResponse("Página de teste de envio de e-mail (implementar lógica aqui).")

def debug_cache_clear(request):
    cache.clear()
    return HttpResponse("Cache limpo com sucesso!")

def debug_session_info(request):
    return HttpResponse(f"Dados da sessão: {dict(request.session.items())}")


# ==============================================================================
# VIEWS DE API PARA AJAX
# ==============================================================================

def api_produtos_autocomplete(request):
    """API para autocomplete de produtos"""
    termo = request.GET.get('q', '').strip()
    
    if len(termo) < 2:
        return JsonResponse({'produtos': []})
    
    produtos = Produto.objects.filter(
        nome__icontains=termo,
        ativo=True,
        quantidade_estoque__gt=0
    ).values('id', 'nome', 'preco')[:10]
    
    return JsonResponse({'produtos': list(produtos)})


def api_carrinho_count(request):
    """API para retornar quantidade de itens no carrinho"""
    carrinho = request.session.get('carrinho', {})
    quantidade = sum(item['quantidade'] for item in carrinho.values())
    return JsonResponse({'quantidade': quantidade})


@require_POST
@csrf_exempt
def api_aplicar_cupom(request):
    """API para aplicar cupom de desconto"""
    data = json.loads(request.body)
    codigo_cupom = data.get('codigo', '').strip().upper()
    valor_pedido = Decimal(data.get('valor_pedido', '0'))
    
    try:
        cupom = Cupom.objects.get(
            codigo=codigo_cupom,
            ativo=True,
            usos_realizados__lt=F('limite_uso')
        )
        
        # Verificar validade
        if cupom.data_validade and cupom.data_validade < timezone.now().date():
            return JsonResponse({'success': False, 'message': 'Cupom expirado.'})
        
        # Verificar valor mínimo
        if valor_pedido < cupom.valor_minimo_compra:
            return JsonResponse({
                'success': False, 
                'message': f'Valor mínimo para este cupom: R$ {cupom.valor_minimo_compra}'
            })
        
        # Calcular desconto
        if cupom.tipo_desconto == Cupom.TipoDesconto.PERCENTUAL:
            desconto = valor_pedido * (cupom.valor_desconto / 100)
        else:
            desconto = cupom.valor_desconto
        
        # Não pode ser maior que o valor do pedido
        desconto = min(desconto, valor_pedido)
        
        return JsonResponse({
            'success': True,
            'desconto': str(desconto),
            'valor_final': str(valor_pedido - desconto),
            'cupom_id': cupom.id,
        })
        
    except Cupom.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Cupom inválido.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Erro ao aplicar cupom.'})