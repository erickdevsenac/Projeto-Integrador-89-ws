from django.contrib.auth.models import User
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
            if tipo in ['FORNECEDOR', 'ONG']:
                if not cnpj:
                    mensagem = "CNPJ é obrigatório para Fornecedores e ONGs."
                    return render(request, "core/cadastro.html", {"mensagem": mensagem})

            user = User.objects.create_user(username=email, email=email, password=senha)
            perfil = Perfil.objects.create(
                usuario=user,
                tipo=tipo,
                nome=nome,
                email=email,
                telefone=telefone,
                endereco=endereco,
                cnpj=cnpj if tipo in ['FORNECEDOR', 'ONG'] else None,
                descricao_parceiro=descricao_parceiro if tipo in ['FORNECEDOR', 'ONG'] else ''
            )

            mensagem = "Usuário cadastrado com sucesso!"
            return redirect('telalogin')

    return render(request, "core/cadastro.html", {"mensagem": mensagem})

def trocasenha(request):
    return render(request, 'core/senha_erica.html')
def telalogin(request):
    mensagem = ""

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=email)  
            if check_password(password, user.password):
                request.session['usuario_id'] = user.id
                return redirect('index')
            else:
                mensagem = "Senha ou email incorretos."
        except User.DoesNotExist:
            mensagem = "Usuário não encontrado."

    return render(request, "core/telalogin.html", {"mensagem": mensagem})
def receitas(request):
    return render (request, 'core/receitas.html')

def videos(request):
    return render (request, 'core/videos.html')