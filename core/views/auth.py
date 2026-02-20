import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.http import require_http_methods

from core.forms import (
    CadastroStep1Form,
    CompleteClientProfileForm,
    CompletePartnerProfileForm,
)
from core.models import Pedido, PedidoVendedor, Perfil, Produto

logger = logging.getLogger(__name__)


def cadastro(request):
    if request.method == "POST":
        form = CadastroStep1Form(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(
                username=data["email"], email=data["email"], password=data["senha"]
            )
            Perfil.objects.create(usuario=user, tipo=data["tipo"])
            user.is_active = False
            user.save()

            # --- Início da Lógica de Envio de E-mail ---
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = f"http://{request.get_host()}/ativar-conta/{uid}/{token}/"

            subject = "Ative sua conta"
            html_body = render_to_string(
                "core/ativacao_conta.html",
                {"user": user, "activation_link": activation_link},
            )
            plain_body = strip_tags(html_body)

            try:
                send_mail(
                    subject,
                    plain_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=html_body,
                )
                messages.success(
                    request,
                    "Cadastro realizado! Um link de ativação foi enviado para o seu e-mail.",
                )
            except Exception as e:
                messages.error(
                    request,
                    "Houve um problema ao enviar o e-mail de ativação. Contate o suporte",
                )
                user.delete()
                return render(request, "core/cadastro_step1.html", {"form": form})

            return redirect("core:login")
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


@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    View de login sem mensagem de boas-vindas automática.
    """
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        senha = request.POST.get("password", "")

        if not email or not senha:
            messages.error(request, "E-mail e senha são obrigatórios.")
            return render(request, "core/login.html")

        try:
            user = authenticate(request, username=email, password=senha)

            if user is None:
                messages.error(request, "Email ou senha incorretos.")
                return render(request, "core/login.html")

            if not user.is_active:
                messages.warning(
                    request,
                    "Sua conta ainda não foi ativada. "
                    "Verifique seu e-mail para ativar.",
                )
                return render(request, "core/login.html")

            # Login bem-sucedido SEM mensagem
            login(request, user)

            # Redirecionar sem mensagem de boas-vindas
            next_url = request.GET.get("next", "core:index")
            return redirect(next_url)

        except Exception as e:
            logger.error(
                f"Erro no login para {email}: {type(e).__name__} - {str(e)}",
                exc_info=True,
            )

            messages.error(
                request,
                "Ocorreu um erro ao processar seu login. "
                "Tente novamente ou contate o suporte.",
            )
            return render(request, "core/login.html")

    return render(request, "core/login.html")


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
        dashboard_context["ultimos_pedidos"] = PedidoVendedor.objects.filter(
            vendedor=perfil
        ).order_by("-data_criacao")[:5]
        dashboard_context["baixo_estoque"] = Produto.objects.filter(
            vendedor=perfil, ativo=True, quantidade_estoque__lte=F("estoque_minimo")
        ).order_by("quantidade_estoque")
    elif perfil.tipo == Perfil.TipoUsuario.CLIENTE:
        dashboard_context["ultimos_pedidos"] = Pedido.objects.filter(
            cliente=perfil
        ).order_by("-data_criacao")[:5]

    context = {"form": form, "perfil": perfil, "dashboard": dashboard_context}

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
    """Solicita recuperação de senha via email."""
    if request.method == "POST":
        email = request.POST.get("email")

        if not email:
            messages.error(request, "Por favor, informe um e-mail válido.")
            return render(request, "core/recuperarsenha.html")

        try:
            usuario = User.objects.get(email=email)

            # Gerar token seguro
            uid = urlsafe_base64_encode(force_bytes(usuario.pk))
            token = default_token_generator.make_token(usuario)

            # Construir link completo
            link_path = reverse(
                "core:password_reset_confirm", kwargs={"uidb64": uid, "token": token}
            )
            link_completo = f"{request.scheme}://{request.get_host()}{link_path}"

            # Corpo do email
            corpo_texto = f"""
Olá, {usuario.first_name or usuario.username}!

Você solicitou a redefinição de senha no Aproveite Mais.

Clique no link abaixo para criar uma nova senha:
{link_completo}

Este link expira em 24 horas.

Se você não solicitou esta alteração, ignore este e-mail.

---
Equipe Aproveite Mais
            """

            # Enviar email
            try:
                send_mail(
                    subject="Redefinição de senha - Aproveite Mais",
                    message=corpo_texto,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[usuario.email],
                    fail_silently=False,
                )
                messages.success(
                    request, "E-mail enviado! Verifique sua caixa de entrada e spam."
                )
            except Exception as e:
                messages.error(
                    request, "Erro ao enviar e-mail. Tente novamente mais tarde."
                )
                print(f"Erro ao enviar email: {e}")

        except User.DoesNotExist:
            # Segurança: não revelar se email existe
            messages.success(
                request, "E-mail enviado! Verifique sua caixa de entrada e spam."
            )

        # Sempre redireciona para login
        return redirect("core:login")

    return render(request, "core/recuperarsenha.html")


def redefinir_senha_confirmar(request, uidb64, token):
    """Confirma token e permite redefinir senha."""
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Validar token
    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, "Link de redefinição inválido ou expirado.")
        return render(request, "core/redefinir_senha.html", {"validlink": False})

    if request.method == "POST":
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Senha redefinida com sucesso! Faça login com sua nova senha."
            )
            return redirect("core:login")
        else:
            # Exibir erros do formulário
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = SetPasswordForm(user)

    return render(
        request, "core/redefinir_senha.html", {"form": form, "validlink": True}
    )


@login_required
def alterarsenha(request):
    """
    Permite usuário logado alterar sua própria senha.
    Mantém usuário logado após alteração.
    """
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)

        if form.is_valid():
            # Salvar nova senha
            user = form.save()

            # ✅ Manter usuário logado após alteração
            update_session_auth_hash(request, user)

            logger.info(f"Senha alterada pelo usuário: {user.email} (ID: {user.pk})")

            messages.success(
                request, "✅ Sua senha foi alterada com sucesso! Você continua logado."
            )
            return redirect("core:alterarsenha")  # Redireciona para a mesma página
        else:
            # Exibir erros do formulário
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "core/alterarsenha.html", {"form": form})


def ativar_conta(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(
            request, "Conta ativada com sucesso! Por favor, complete seu perfil."
        )
        return redirect("core:completar_cadastro")
    else:
        messages.error(request, "Link de ativação inválido ou expirado.")
        return redirect("core:login")
