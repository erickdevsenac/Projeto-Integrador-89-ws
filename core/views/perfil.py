from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from core.models import Perfil
from core.forms import CompleteClientProfileForm, CompletePartnerProfileForm


@login_required
def perfil_detail(request):
    """
    Exibe a página de perfil do usuário logado e permite a edição.
    """
    perfil, created = Perfil.objects.get_or_create(usuario=request.user)

    if perfil.tipo == 'CLIENTE':
        FormClass = CompleteClientProfileForm
    elif perfil.tipo == 'VENDEDOR':
        FormClass = CompletePartnerProfileForm
    else:
        FormClass = None

    form = None

    if FormClass:
        if request.method == 'POST':
            form = FormClass(request.POST, request.FILES, instance=perfil)
            if form.is_valid():
                form.save()
                return redirect('core:perfil')
        else:
            form = FormClass(instance=perfil)

    dashboard_data = {
        "baixo_estoque": [],
        "ultimos_pedidos": []
    }

    context = {
        "perfil": perfil,
        "dashboard": dashboard_data,
        "form": form,
        "user": request.user,  
    }

    return render(request, "core/perfil.html", context)
