from .models import Receita, Produto
from .forms import CadastroForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

def index(request):
    return render(request, 'core/index.html')

def produtos(request):
    return render(request, 'core/produtos.html')

def doacao(request):
    return render(request, 'core/doacao.html')

def contato(request):
    return render(request, 'core/contato.html')

def cadastro(request):
    if request.method == "POST":
        form = CadastroForm(request.POST)
        if form.is_valid():
            # Dados já estão limpos e validados pelo form
            data = form.cleaned_data

            # Cria o User
            user = User.objects.create_user(
                username=data['email'],
                email=data['email'],
                password=data['senha']
            )

            # Salva o Perfil (note que o form é do tipo ModelForm)
            perfil = form.save(commit=False)
            perfil.usuario = user
            perfil.save()

            login(request, user)
            return redirect('index')
    else:
        form = CadastroForm()

    return render(request, "core/cadastro.html", {"form": form})

def trocasenha(request):
    return render(request, 'core/senha_erica.html')

def telalogin(request):
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

def receitas(request):
    lista_receitas = Receita.objects.filter(disponivel=True).order_by('-data_criacao')

    context = {
        'receitas': lista_receitas,
    }
    
    return render(request, 'core/receitas.html', context)

def videos(request):
    return render (request, 'core/videos.html')


def buscar_produtos(request):
    termo = request.GET.get('termo', '')
    resultados = Produto.objects.filter(nome__icontains=termo) if termo else []

    return render(request, 'core/resultados_busca.html', {
        'resultados': resultados,
        'termo': termo,
     })
    
def cadastroproduto(request):
    return render (request, 'core/cadastroproduto.html')