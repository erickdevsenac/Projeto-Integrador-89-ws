from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .models import Perfil
from django.contrib.auth.hashers import check_password


def index(request):
    return render(request, 'core/index.html')

def produtos(request):
    return render(request, 'core/produtos.html')

def contato(request):
    return render(request, 'core/contato.html')

def cadastro(request):
    mensagem = ""

    if request.method == "POST":
        tipo = request.POST.get("tipo")
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        senha = request.POST.get("senha")
        confirmar = request.POST.get("confirmar")
        telefone = request.POST.get("telefone")
        endereco = request.POST.get("endereco")
        cnpj = request.POST.get("cnpj")
        descricao_parceiro = request.POST.get("descricao_parceiro")

        if senha != confirmar:
            mensagem = "As senhas não conferem!"
        elif User.objects.filter(username=email).exists():
            mensagem = "Este e-mail já está cadastrado!"
        else:
            if tipo in ['VENDEDOR', 'ONG'] and not cnpj:
                mensagem = "CNPJ é obrigatório para Vendedores e ONGs."
                return render(request, "core/cadastro.html", {"mensagem": mensagem})

            user = User.objects.create_user(username=email, email=email, password=senha)
            user.first_name = nome
            user.save()

            Perfil.objects.create(
                usuario=user,
                tipo=tipo,
                telefone=telefone,
                endereco=endereco,
                cnpj=cnpj if tipo in ['VENDEDOR', 'ONG'] else None,
                descricao_parceiro=descricao_parceiro if tipo in ['VENDEDOR', 'ONG'] else ''
            )
            
            login(request, user)
            return redirect('index')

    return render(request, "core/cadastro.html", {"mensagem": mensagem})

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
    return render (request, 'core/receitas.html')

def videos(request):
    return render (request, 'core/videos.html')