from .models import Receita, Produto, Perfil, Pedido, ItemPedido,PedidoVendedor
from django.contrib.auth.decorators import login_required
from .forms import CadastroForm, ReceitaForm, IngredienteFormSet, EtapaPreparoFormSet
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal
from django.core.paginator import Paginator
from django.contrib import messages

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
    return render(request, 'core/contato.html')

def doacao(request):
    ongs = Perfil.objects.filter(tipo = "ONG").all()
    context = {
        "instituicoes": ongs
    }
    return render(request, 'core/doacao.html', context)

def cadastro(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            try:
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
                return redirect('core:index')
            except Exception as e:
                    form.add_error(None, f"Erro ao criar conta: {str(e)}")
    else:
        form = CadastroForm()
 
    return render(request, "core/cadastro.html", {"form": form})
 
 
def alterarsenha(request):
    return render(request, 'core/alterarsenha.html')
 
def login_view(request):
    mensagem = ""
    if request.method == "POST":
        email = request.POST.get("email")
        senha = request.POST.get("password")
        
        user = authenticate(request, username=email, password=senha)

        if user is not None:
            # Agora a chamada para login() não é mais ambígua
            login(request, user) 
            return redirect('core:index')
        else:
            mensagem = "Email ou senha incorretos."

    return render(request, "core/telalogin.html", {"mensagem": mensagem})
 
def logout_view(request):
    logout(request)
    return redirect('core:index')

def receitas(request):
    lista_receitas = Receita.objects.filter(disponivel=True).order_by('-data_criacao')

    context = {
        'receitas': lista_receitas,
    }
    
    return render(request, 'core/receitas.html', context)

def videos(request):
    return render (request, 'core/videos.html')


def buscarprodutos(request):
    termo = request.GET.get('termo', '')
    resultados = Produto.objects.filter(nome__icontains=termo) if termo else []

    return render(request, 'core/resultados_busca.html', {
        'resultados': resultados,
        'termo': termo,
     })
    
def cadastroproduto(request):
    return render (request, 'core/cadastroproduto.html')


@login_required
def cria_receita(request):
    # Se a requisição for POST, o usuário está enviando o formulário
    if request.method == 'POST':
        # Instancia o formulário principal e os formsets com os dados enviados
        form = ReceitaForm(request.POST, request.FILES)
        ingrediente_formset = IngredienteFormSet(request.POST, prefix='ingredientes')
        etapa_formset = EtapaPreparoFormSet(request.POST, prefix='etapas')

        # Valida todos os formulários
        if form.is_valid() and ingrediente_formset.is_valid() and etapa_formset.is_valid():
            # Salva o formulário principal, mas não comita no banco ainda
            receita = form.save(commit=False)
            receita.autor = request.user  # Associa o usuário logado como autor
            receita.save() # Agora salva a receita no banco

            # Associa os formsets à instância da receita recém-criada
            ingrediente_formset.instance = receita
            etapa_formset.instance = receita

            # Salva os formsets no banco de dados
            ingrediente_formset.save()
            etapa_formset.save()

            # Redireciona para uma página de sucesso (ex: minhas receitas)
            return redirect('core:index') # Altere para a URL desejada

    # Se a requisição for GET, o usuário está visitando a página pela primeira vez
    else:
        # Cria instâncias em branco do formulário e dos formsets
        form = ReceitaForm()
        ingrediente_formset = IngredienteFormSet(prefix='ingredientes')
        etapa_formset = EtapaPreparoFormSet(prefix='etapas')

    context = {
        'form': form,
        'ingrediente_formset': ingrediente_formset,
        'etapa_formset': etapa_formset,
    }
    
    return render(request, 'receitas/cria_receita.html', context)


def ver_carrinho(request):
    print(f"Ver - Session Key: {request.session.session_key}")
    # Pega o carrinho da sessão. O valor padrão deve ser um dicionário VAZIO.
    carrinho = request.session.get('carrinho', {})
    
    carrinho_detalhado = []
    total_carrinho = Decimal('0.00')

    for produto_id, item_info in carrinho.items():
        preco_unitario = Decimal(item_info['preco'])
        quantidade = item_info['quantidade']
        
        # Calculamos o subtotal
        subtotal = quantidade * preco_unitario
        
        carrinho_detalhado.append({
            'produto_id': produto_id,
            'nome': item_info['nome'],
            'quantidade': quantidade,
            'preco': preco_unitario,
            'imagem_url': item_info.get('imagem_url', ''),
            'subtotal': subtotal,
        })
        
        total_carrinho += subtotal

    context = {
        'carrinho': carrinho_detalhado,
        'total_carrinho': total_carrinho,
    }

    return render(request, 'core/carrinho.html', context)

def adicionar_carrinho(request, produto_id):
    print(f"Adicionar - Session Key: {request.session.session_key}")
    produto = get_object_or_404(Produto, id=produto_id)
    carrinho = request.session.get('carrinho', {})
    quantidade_solicitada = int(request.POST.get('quantidade', 1))
    produto_id_str = str(produto.id)

    # --- LÓGICA DE VERIFICAÇÃO DE ESTOQUE ---
    quantidade_no_carrinho = carrinho.get(produto_id_str, {}).get('quantidade', 0)
    quantidade_total_desejada = quantidade_no_carrinho + quantidade_solicitada

    if quantidade_total_desejada > produto.quantidade_estoque:
        # 2. Adiciona uma mensagem de erro
        messages.error(request, f"Desculpe, temos apenas {produto.quantidade_estoque} unidades de '{produto.nome}' em estoque.")
        # Redireciona de volta para a página anterior
        return redirect(request.META.get('HTTP_REFERER', 'core:produtos'))
    # --- FIM DA VERIFICAÇÃO ---

    # Se o estoque for suficiente, continua com a lógica normal
    if produto_id_str in carrinho:
        carrinho[produto_id_str]['quantidade'] = quantidade_total_desejada
    else:
        carrinho[produto_id_str] = {
            'quantidade': quantidade_total_desejada,
            'preco': str(produto.preco),
            'nome': produto.nome,
            'imagem_url': produto.imagem.url if produto.imagem else '',
        }

    request.session['carrinho'] = carrinho
    
    # Esta linha continua sendo uma boa prática para garantir o salvamento
    request.session.modified = True
    
    # 3. Adiciona uma mensagem de sucesso
    messages.success(request, f"'{produto.nome}' foi adicionado ao seu carrinho!")
    
    return redirect('core:ver_carrinho')


@login_required
def finalizar_pedido(request):
    carrinho_session = request.session.get('carrinho', {})
    if not carrinho_session:
        messages.error(request, "Seu carrinho está vazio.")
        return redirect('core:produtos')

    # Preparar dados do carrinho para exibição (mesma lógica da ver_carrinho)
    carrinho_detalhado = []
    total_carrinho = Decimal('0.00')
    for produto_id, item_info in carrinho_session.items():
        subtotal = Decimal(item_info['preco']) * item_info['quantidade']
        total_carrinho += subtotal
        carrinho_detalhado.append({
            'produto_id': produto_id,
            'nome': item_info['nome'],
            'quantidade': item_info['quantidade'],
            'preco': Decimal(item_info['preco']),
            'subtotal': subtotal
        })

    # Se a requisição for POST, o usuário confirmou a compra
    if request.method == 'POST':
        try:
            # transaction.atomic garante que todas as operações no banco de dados
            # sejam executadas com sucesso. Se qualquer uma falhar, todas são revertidas.
            with transaction.atomic():
                cliente_perfil = request.user.perfil

                # 1. Cria o Pedido principal
                pedido = Pedido.objects.create(
                    cliente=cliente_perfil,
                    valor_total=total_carrinho,
                    endereco_entrega=cliente_perfil.endereco # Usando o endereço do perfil
                )

                # 2. Agrupa os itens do carrinho por vendedor
                pedidos_por_vendedor = {}
                for item in carrinho_detalhado:
                    produto = Produto.objects.get(id=item['produto_id'])
                    vendedor_perfil = produto.vendedor

                    if vendedor_perfil not in pedidos_por_vendedor:
                        pedidos_por_vendedor[vendedor_perfil] = {
                            'itens': [],
                            'subtotal': Decimal('0.00')
                        }
                    
                    pedidos_por_vendedor[vendedor_perfil]['itens'].append(item)
                    pedidos_por_vendedor[vendedor_perfil]['subtotal'] += item['subtotal']

                # 3. Cria os Pedidos de Vendedor (sub-pedidos) e os Itens do Pedido
                for vendedor, dados_pedido in pedidos_por_vendedor.items():
                    sub_pedido = PedidoVendedor.objects.create(
                        pedido_principal=pedido,
                        vendedor=vendedor,
                        valor_subtotal=dados_pedido['subtotal']
                    )

                    for item_data in dados_pedido['itens']:
                        produto = Produto.objects.get(id=item_data['produto_id'])
                        ItemPedido.objects.create(
                            sub_pedido=sub_pedido,
                            produto=produto,
                            quantidade=item_data['quantidade'],
                            preco_unitario=item_data['preco']
                        )
                        # 4. Atualiza o estoque
                        produto.quantidade_estoque -= item_data['quantidade']
                        produto.save()

                # 5. Limpa o carrinho da sessão
                del request.session['carrinho']
                messages.success(request, "Seu pedido foi finalizado com sucesso!")
                # Redireciona para uma página de "meus pedidos" (a ser criada)
                return redirect('core:index') # Mude para 'meus_pedidos' no futuro

        except Exception as e:
            messages.error(request, f"Ocorreu um erro ao finalizar seu pedido: {e}")
            return redirect('core:ver_carrinho')

    # Se a requisição for GET, apenas mostra a página de confirmação
    context = {
        'carrinho': carrinho_detalhado,
        'total_carrinho': total_carrinho,
    }
    return render(request, 'core/checkout.html', context)

