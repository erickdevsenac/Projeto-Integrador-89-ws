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
from django.db.models import F

from core.forms import CadastroStep1Form, CompleteClientProfileForm, CompletePartnerProfileForm

from core.models import Perfil, Pedido, PedidoVendedor, Produto

def cadastro(request):
    if request.method == "POST":
        form = CadastroStep1Form(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(
                username=data["email"], 
                email=data["email"], 
                password=data["senha"]
            )
            Perfil.objects.create(usuario=user, tipo=data["tipo"])
            user.is_active = False
            
            login(request, user)
            
            return redirect('core:completar_cadastro') 
    else:
        form = CadastroStep1Form()
    return render(request, "core/cadastro_step1.html", {"form": form})

@login_required(login_url="/login/")
def completar_cadastro(request):
    perfil = request.user.perfil
    
    if perfil.tipo == Perfil.TipoUsuario.CLIENTE:
        FormClass = CompleteClientProfileForm
    else: 
        FormClass = CompletePartnerProfileForm
        
    if request.method == "POST":
        form = FormClass(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, "Cadastro concluído com sucesso! Bem-vindo(a)!")
            return redirect("core:index")
    else:
        form = FormClass(instance=perfil)
        
    return render(request, "core/cadastro_step2.html", {"form": form})

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

    if perfil.tipo == Perfil.TipoUsuario.CLIENTE:
        FormClass = CompleteClientProfileForm
    else:  # VENDEDOR ou ONG
        FormClass = CompletePartnerProfileForm
    
    if request.method == "POST":
        form = FormClass(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado com sucesso!")
            return redirect("core:perfil")
    else:
        form = FormClass(instance=perfil)

    dashboard_context = {}
    if perfil.tipo == Perfil.TipoUsuario.VENDEDOR:
        dashboard_context['ultimos_pedidos'] = PedidoVendedor.objects.filter(vendedor=perfil).order_by('-data_criacao')[:5]
        dashboard_context['baixo_estoque'] = Produto.objects.filter(
            vendedor=perfil, 
            ativo=True, 
            quantidade_estoque__lte=F('estoque_minimo')
        ).order_by('quantidade_estoque')
    
    elif perfil.tipo == Perfil.TipoUsuario.CLIENTE:
        dashboard_context['ultimos_pedidos'] = Pedido.objects.filter(cliente=perfil).order_by('-data_criacao')[:5]

    context = {
        'form': form,
        'perfil': perfil,
        'dashboard': dashboard_context
    }
    
    return render(request, "core/perfil.html", context)

@login_required
def configuracoes(request):
    if request.method == "POST":
        if "excluir_conta" in request.POST:
            request.user.delete()
            messages.success(request, "Sua conta foi excluída com sucesso.")
            return redirect("core:index")
        
        elif "salvar_configuracoes" in request.POST:
            for campo in ["tema", "fonte", "acessibilidade", "notificacoes"]:
                valor = request.POST.get(campo)
                if valor is not None: 
                    request.session[campo] = valor
            
            messages.success(request, "Suas configurações foram salvas.")
            return redirect("core:configuracoes")

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

