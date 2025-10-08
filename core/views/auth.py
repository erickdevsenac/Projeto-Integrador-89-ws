from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.mail import send_mail

from core.forms import CadastroForm, PerfilForm
from core.models import Perfil

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
            messages.success(request, f"Bem-vindo(a), {user.username}!")
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
        if user:
            login(request, user)
            return redirect("core:index")
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

@login_required
def configuracoes(request):
    if request.method == "POST":
        if "excluir_conta" in request.POST:
            request.user.delete()
            messages.success(request, "Conta excluída com sucesso.")
            return redirect("core:index")
        for campo in ["tema", "fonte", "acessibilidade", "notificacoes"]:
            valor = request.POST.get(campo)
            if valor:
                request.session[campo] = valor
        messages.success(request, "Configurações atualizadas.")
    return render(request, "core/configuracoes.html")

def recuperarsenha(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            usuario = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'E-mail não encontrado.')
            return render(request, 'core/recuperarsenha.html')

        uid = urlsafe_base64_encode(force_bytes(usuario.pk))
        token = default_token_generator.make_token(usuario)
        link = f"http://{request.get_host()}/redefinir-senha/{uid}/{token}/"
        corpo = render_to_string('email/senha_reset.html', {'usuario': usuario, 'link_de_reset': link})

        send_mail('Redefinição de senha', corpo, 'no-reply@site.com', [usuario.email])
        messages.success(request, 'E-mail enviado com instruções.')
        return redirect('core:login_view')
    return render(request, "core/recuperarsenha.html")

def alterarsenha(request):
    return render(request, "core/alterarsenha.html")
