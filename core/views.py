from decimal import Decimal, InvalidOperation
from .models import Avaliacao
from .forms import AvaliacaoForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.core.mail import send_mail

from .forms import (
    CadastroForm,
    CupomForm,
    EtapaPreparoFormSet,
    IngredienteFormSet,
    PerfilForm,
    ProdutoForm,
    ReceitaForm,
)

from .models import (
    Categoria,
    Dica,
    EquipeDev,
    ItemPedido,
    Pedido,
    PedidoVendedor,
    Perfil,
    ProdutoVendedor,
    Receita,
    Produto
)

def is_vendedor(user):
    """Verifica se o usuário é um vendedor autenticado."""
    return (
        user.is_authenticated
        and hasattr(user, "perfil")
        and user.perfil.tipo == Perfil.TipoUsuario.VENDEDOR
    )

def index(request):
    return render(request, 'core/index.html')

def ongs_pagina(request, usuario_id):
    ongs_pagina = get_object_or_404(Perfil, tipo = "ONG", usuario_id = usuario_id)
    context = {
        "inf_ongs": ongs_pagina
    }
    return render(request, 'core/ong_pagina.html', context)

def contato(request):
    return render(request, "core/contato.html")


def devs(request):
    desenvolvedores = EquipeDev.objects.all()
    print (desenvolvedores)
    return render(request, "core/timedev.html", {"equipe": desenvolvedores})


def doacao(request):
    ongs = Perfil.objects.filter(tipo="ONG")
    return render(request, "core/doacao.html", {"instituicoes": ongs})


def videos(request):
    return render(request, "core/videos.html")

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
        if 'excluir_conta' in request.POST:
            request.user.delete()
            messages.success(request, "Sua conta foi excluída com sucesso.")
            return redirect('core:index')

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
        
        messages.success(request, "Configurações atualizadas com sucesso!")
        return redirect('core:configuracoes')

    return render(request, "core/configuracoes.html")


def recuperarsenha(request):
    if request.method == 'POST':
        email_do_usuario = request.POST.get('email')
    
        try:
            usuario = User.objects.get(email=email_do_usuario)
        except User.DoesNotExist:
            messages.error(request, 'Não há conta associada a este e-mail.')
            return render(request, 'core/recuperarsenha.html')
            
        uid = urlsafe_base64_encode(force_bytes(usuario.pk))
        token = default_token_generator.make_token(usuario)
        
        current_site = request.get_host()
        link_de_reset = f"http://{current_site}/redefinir-senha/{uid}/{token}/"
        
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
            messages.success(request, 'Um e-mail com instruções foi enviado. Verifique sua caixa de entrada.')
            return redirect('core:login_view') 
        except Exception as e:
            messages.error(request, f'Ocorreu um erro ao enviar o e-mail: {e}')
    return render(request, "core/recuperarsenha.html")

def alterarsenha(request):
    return render(request, "core/alterarsenha.html")


def produtos(request):
    """
    Lista todos os produtos disponíveis, com suporte a paginação e filtro por categoria.
    Esta é a versão correta e completa.
    """
    lista_produtos = Produto.objects.filter(
        ativo=True, quantidade_estoque__gt=0
    ).order_by("-data_criacao")
    
    categorias = Categoria.objects.all()

    categoria_slug = request.GET.get("categoria")
    if categoria_slug:
        lista_produtos = lista_produtos.filter(categoria__slug=categoria_slug)

    paginator = Paginator(lista_produtos, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "categorias": categorias,
        "categoria_atual": categoria_slug,
    }
    return render(request, "core/produtos.html", context)


def buscar_produtos(request):
    termo = request.GET.get("termo", "")
    if termo:
        resultados = ProdutoVendedor.objects.filter(nome__icontains=termo, ativo=True)
    else:
        resultados = []
        
    paginator = Paginator(resultados, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(
        request,
        "core/resultados_busca.html",
        {"page_obj": page_obj, "termo": termo},
    )

@user_passes_test(is_vendedor, login_url="/login/")
def cadastroproduto(request):
    if request.method == "POST":
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            produto = form.save(commit=False)
            produto.vendedor = request.user.perfil
            produto.save()
            messages.success(
                request, f"Produto '{produto.nome}' cadastrado com sucesso!"
            )
            return redirect("core:produtos")
    else:
        form = ProdutoForm()
    return render(request, "core/cadastroproduto.html", {"form": form})



def ver_carrinho(request):
    carrinho_session = request.session.get("carrinho", {})
    carrinho_detalhado = []
    total_carrinho = Decimal("0.00")
    keys_para_remover = []

    for produto_id, item_info in carrinho_session.items():
        if not produto_id or not produto_id.isdigit():
            keys_para_remover.append(produto_id)
            continue
        
        try:
            preco_unitario = Decimal(item_info["preco"])
            quantidade = item_info["quantidade"]
            subtotal = quantidade * preco_unitario
            
            carrinho_detalhado.append(
                {
                    "produto_id": produto_id,
                    "nome": item_info["nome"],
                    "quantidade": quantidade,
                    "preco": preco_unitario,
                    "imagem_url": item_info.get("imagem_url", ""),
                    "subtotal": subtotal,
                    "vendedor_nome": item_info.get("vendedor_nome", "N/A"),
                }
            )
            total_carrinho += subtotal
        except (KeyError, InvalidOperation, TypeError):
             keys_para_remover.append(produto_id)
             continue

    if keys_para_remover:
        for key in keys_para_remover:
            if key in carrinho_session:
                del carrinho_session[key]
        request.session["carrinho"] = carrinho_session
        request.session.modified = True

    return render(
        request,
        "core/carrinho.html",
        {"carrinho": carrinho_detalhado, "total_carrinho": total_carrinho},
    )


@require_POST
def adicionar_carrinho(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    carrinho = request.session.get("carrinho", {})
    
    try:
        quantidade_solicitada = int(request.POST.get("quantidade", 1))
        if quantidade_solicitada <= 0:
            messages.error(request, "A quantidade deve ser positiva.")
            return redirect(request.META.get("HTTP_REFERER", "core:produtos"))
    except ValueError:
        messages.error(request, "Quantidade inválida.")
        return redirect(request.META.get("HTTP_REFERER", "core:produtos"))
        
    produto_id_str = str(produto.id)
    quantidade_no_carrinho = carrinho.get(produto_id_str, {}).get("quantidade", 0)
    quantidade_total_desejada = quantidade_no_carrinho + quantidade_solicitada

    if quantidade_total_desejada > produto.quantidade_estoque:
        messages.error(
            request,
            f"Desculpe, temos apenas {produto.quantidade_estoque} unidades de '{produto.nome}' em estoque.",
        )
        return redirect(request.META.get("HTTP_REFERER", "core:produtos"))

    if produto_id_str in carrinho:
        carrinho[produto_id_str]["quantidade"] = quantidade_total_desejada
    else:
        carrinho[produto_id_str] = {
            "quantidade": quantidade_total_desejada,
            "preco": str(produto.preco),
            "nome": produto.nome,
            "imagem_url": produto.imagem.url if produto.imagem else "",
            "vendedor_nome": produto.vendedor.nome_negocio if produto.vendedor else "N/A",
        }
    request.session["carrinho"] = carrinho
    request.session.modified = True
    messages.success(request, f"'{produto.nome}' foi adicionado ao seu carrinho!")
    return redirect("core:ver_carrinho")


@require_POST
def atualizar_carrinho(request):
    carrinho = request.session.get("carrinho", {})

    # Percorre todos os itens enviados pelo formulário
    for key, value in request.POST.items():
        # Procuramos por chaves que começam com 'quantidade_'
        if key.startswith("quantidade_"):
            produto_id_str = key.split("_")[1]
            try:
                nova_quantidade = int(value)
            except ValueError:
                continue

            if produto_id_str in carrinho:
                try:
                    produto = ProdutoVendedor.objects.get(id=int(produto_id_str))

                    if nova_quantidade > produto.quantidade_estoque:
                        messages.error(
                            request,
                            f"Estoque insuficiente para '{produto.nome}'. Apenas {produto.quantidade_estoque} disponíveis.",
                        )
                        continue

                    if nova_quantidade > 0:
                        carrinho[produto_id_str]["quantidade"] = nova_quantidade
                    else:
                        del carrinho[produto_id_str]
                        messages.info(request, f"Item '{produto.nome}' removido.")

                except ProdutoVendedor.DoesNotExist:
                    del carrinho[produto_id_str]
                    messages.warning(request, "Um item do catálogo foi removido do seu carrinho.")

    request.session["carrinho"] = carrinho
    request.session.modified = True
    messages.success(request, "Carrinho atualizado com sucesso!")
    return redirect("core:ver_carrinho")


def remover_item(request, produto_id):
    carrinho = request.session.get("carrinho", {})
    produto_id_str = str(produto_id)
    if produto_id_str in carrinho:
        nome_produto = carrinho[produto_id_str].get("nome", "Item")
        del carrinho[produto_id_str]
        request.session["carrinho"] = carrinho
        request.session.modified = True
        messages.success(request, f"'{nome_produto}' removido do carrinho.")
    return redirect("core:ver_carrinho")

@login_required(login_url="/login/")
def finalizar_pedido(request):
    carrinho_session = request.session.get("carrinho", {})
    if not carrinho_session:
        messages.error(request, "Seu carrinho está vazio.")
        return redirect("core:produtos")

    carrinho_detalhado = []
    total_carrinho = Decimal("0.00")
    
    for produto_id, item_info in carrinho_session.items():
        try:
            subtotal = Decimal(item_info["preco"]) * item_info["quantidade"]
            total_carrinho += subtotal
            carrinho_detalhado.append(
                {
                    "produto_id": produto_id,
                    "quantidade": item_info["quantidade"],
                    "preco": Decimal(item_info["preco"]),
                    "subtotal": subtotal,
                    "nome": item_info["nome"],
                }
            )
        except (KeyError, InvalidOperation, TypeError):
             messages.error(request, "Erro de formatação nos dados do carrinho. Por favor, tente novamente.")
             return redirect("core:ver_carrinho")


    if request.method == "POST":
        try:
            with transaction.atomic():
                cliente_perfil = request.user.perfil
                
                pedido = Pedido.objects.create(
                    cliente=cliente_perfil,
                    valor_total=total_carrinho,
                    endereco_entrega=cliente_perfil.endereco, 
                )
                
                pedidos_por_vendedor = {}
                
                for item in carrinho_detalhado:
                    produto = Produto.objects.select_for_update().get(id=item["produto_id"])
                    
                    if produto.quantidade_estoque < item["quantidade"]:
                         raise Exception(f"Estoque insuficiente para {produto.nome}. Apenas {produto.quantidade_estoque} disponíveis.")
                         
                    vendedor_perfil = produto.vendedor
                    
                    if vendedor_perfil not in pedidos_por_vendedor:
                        pedidos_por_vendedor[vendedor_perfil] = {
                            "itens": [],
                            "subtotal": Decimal("0.00"),
                        }
                    
                    pedidos_por_vendedor[vendedor_perfil]["itens"].append(item)
                    pedidos_por_vendedor[vendedor_perfil]["subtotal"] += item["subtotal"]

                for vendedor, dados_pedido in pedidos_por_vendedor.items():
                    sub_pedido = PedidoVendedor.objects.create(
                        pedido_principal=pedido,
                        vendedor=vendedor,
                        valor_subtotal=dados_pedido["subtotal"],
                    )
                    
                    for item_data in dados_pedido["itens"]:
                        produto = Produto.objects.get(id=item_data["produto_id"])
                        
                        ItemPedido.objects.create(
                            sub_pedido=sub_pedido,
                            produto=produto,
                            quantidade=item_data["quantidade"],
                            preco_unitario=item_data["preco"],
                        )
                        
                        produto.quantidade_estoque -= item_data["quantidade"]
                        produto.save()
                        
                del request.session["carrinho"]
                messages.success(request, f"Seu pedido #{pedido.id} foi finalizado com sucesso!")
                return redirect("core:meus_pedidos")
                
        except Exception as e:
            messages.error(request, f"Ocorreu um erro ao finalizar seu pedido: {e}")
            return redirect("core:ver_carrinho")

    return render(
        request,
        "core/checkout.html",
        {"carrinho": carrinho_detalhado, "total_carrinho": total_carrinho},
    )


@login_required(login_url="/login/")
def meus_pedidos(request):
    try:
        perfil_usuario = request.user.perfil
    except Perfil.DoesNotExist:
        messages.error(request, "Seu perfil não foi encontrado.")
        return redirect("core:index")

    if perfil_usuario.tipo == Perfil.TipoUsuario.CLIENTE:
        pedidos = Pedido.objects.filter(cliente=perfil_usuario).order_by("-data_pedido")
        context = {"pedidos": pedidos, "is_cliente": True}
        print(pedidos)
    elif perfil_usuario.tipo == Perfil.TipoUsuario.VENDEDOR:
        pedidos = Pedido.objects.filter(vendedor=perfil_usuario).order_by("-id")
        context = {"pedidos": pedidos, "is_cliente": False}
    else:
        context = {"pedidos": []}
        
    return render(request, "core/meus_pedidos.html", context)

def receitas(request):
    lista_receitas = Receita.objects.filter(disponivel=True).order_by('-data_criacao')
    
    paginator = Paginator(lista_receitas, 9)
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
    lista_dicas = Dica.objects.filter(publicada=True).order_by('-data_publicacao')
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
            messages.success(request, f"Receita '{receita.titulo}' criada com sucesso!")
            return redirect("core:receitas")
        else:
            messages.error(request, "Erro ao criar receita. Por favor, verifique os campos.")
            
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

def is_admin(user):
    return user.is_staff


@user_passes_test(is_admin, login_url="/login/")
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


def notificacao(request):
    return render(request,"core/notificacoes.html")

def vendedor(request):
    return render(request,"core/vendedor.html")

def avaliacao(request):
    avaliacoes = Avaliacao.objects.all().order_by('-data_avaliacao')
    
    paginator = Paginator(avaliacoes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/avaliacao.html', {'page_obj': page_obj})


@login_required
def nova_avaliacao(request):
    """
    Permite que um usuário autenticado crie uma nova avaliação.
    Corrigida para usar mensagens e redirecionar corretamente.
    """
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.usuario = request.user 
            avaliacao.save()  
            messages.success(request, 'Sua avaliação foi enviada com sucesso! ✨')
            return redirect('core:avaliacao') 
        else:
            messages.error(request, 'Não foi possível enviar a avaliação. Por favor, verifique os dados.')
        
    else:
        form = AvaliacaoForm()

    return render(request, 'core/nova_avaliacao.html', {'form': form})