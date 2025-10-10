from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache
from django.http import HttpResponse
from core.forms import CupomForm

def is_admin(user):
    return user.is_staff

# @user_passes_test(is_admin, login_url="/login/")
def criar_cupom(request):
    form = CupomForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Cupom criado com sucesso!")
        return redirect("core:index")
    return render(request, "core/cupom.html", {"form": form})

def debug_email_test(request):
    return HttpResponse("Teste de e-mail OK.")

def debug_cache_clear(request):
    cache.clear()
    return HttpResponse("Cache limpo com sucesso!")

def debug_session_info(request):
    return HttpResponse(f"Dados da sessão: {dict(request.session.items())}")
