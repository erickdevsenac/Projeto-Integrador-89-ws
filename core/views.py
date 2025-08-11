from .models import Receita, Produto, Perfil
from .forms import CadastroForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect


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
 
def login(request):
    mensagem = ""
    if request.method == "POST":
        email = request.POST.get("email")
        senha = request.POST.get("password")
 
        # `authenticate` verifica se o usuário existe E se a senha está correta.
        # Note que estamos usando o 'username=email', pois no cadastro você atribuiu o email ao username.
        user = authenticate(request, username=email, password=senha)
 
        if user is not None:
            # `login` cria a sessão segura para o usuário.
            login(request, user)
            # Redireciona para a página principal após o login bem-sucedido.
            return redirect('index')
        else:
            # Se `authenticate` retornar None, o usuário não existe ou a senha está errada.
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


# def cria_receita(request):
#     if request.method == 'POST':
#         form = ReceitaForm(request.POST, request.FILES)
#         if form.is_valid():
#             receita = form.save(commit=False)
#             receita.pessoa = request.user
#             receita.save()
#             return redirect('minhas_receitas')
#     else:
#         form = ReceitaForm()
#     return render(request, 'receitas/cria_receita.html', {'form': form})