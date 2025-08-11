from .models import Receita, Produto, Perfil
from django.contrib.auth.decorators import login_required
from .forms import CadastroForm, ReceitaForm, IngredienteFormSet, EtapaPreparoFormSet
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from decimal import Decimal

def index(request):
    return render(request, 'core/index.html')

def produtos(request):
    return render(request, 'core/produtos.html')

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
            return redirect('index')
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
            return redirect('index')
        else:
            mensagem = "Email ou senha incorretos."

    return render(request, "core/telalogin.html", {"mensagem": mensagem})
 
def logout_view(request):
    """
    Desconecta o usuário e o redireciona para a página principal.
    """
    logout(request)
    return redirect('index')

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
            return redirect('index') # Altere para a URL desejada

    # Se a requisição for GET, o usuário está visitando a página pela primeira vez
    else:
        # Cria instâncias em branco do formulário e dos formsets
        form = ReceitaForm()
        ingrediente_formset = IngredienteFormSet(prefix='ingredientes')
        etapa_formset = EtapaPreparoFormSet(prefix='etapas')

    # Prepara o contexto para enviar ao template
    context = {
        'form': form,
        'ingrediente_formset': ingrediente_formset,
        'etapa_formset': etapa_formset,
    }
    
    return render(request, 'receitas/cria_receita.html', context)

# Supondo que você tenha renomeado a view para 'ver_carrinho' como no passo a passo anterior
def ver_carrinho(request):
    # Pega o carrinho da sessão. O valor padrão deve ser um dicionário VAZIO.
    carrinho = request.session.get('carrinho', {})
    
    carrinho_detalhado = []
    total_carrinho = Decimal('0.00')

    # CORREÇÃO DO LOOP: Iteramos pegando a chave (produto_id) e o valor (item_info)
    for produto_id, item_info in carrinho.items():
        # Acessamos os dados DENTRO do dicionário 'item_info'
        preco_unitario = Decimal(item_info['preco'])
        quantidade = item_info['quantidade']
        
        # Calculamos o subtotal
        subtotal = quantidade * preco_unitario
        
        # Adicionamos um dicionário limpo ao nosso contexto
        carrinho_detalhado.append({
            'produto_id': produto_id,
            'nome': item_info['nome'],
            'quantidade': quantidade,
            'preco': preco_unitario,
            'imagem_url': item_info.get('imagem_url', ''), # Usar .get() é mais seguro
            'subtotal': subtotal,
        })
        
        total_carrinho += subtotal

    context = {
        'carrinho': carrinho_detalhado,
        'total_carrinho': total_carrinho,
    }

    return render(request, 'core/carrinho.html', context)