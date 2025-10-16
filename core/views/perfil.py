from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from core.models import Perfil


@login_required
def perfil_detail(request):
    """
    Exibe a página de perfil do usuário logado.
    """
    try:
        perfil = request.user.perfil
    except (Perfil.DoesNotExist, AttributeError):
        perfil = None

    dashboard_data = {"baixo_estoque": [], "ultimos_pedidos": []}

    context = {
        "perfil": perfil,
        "dashboard": dashboard_data,
        "form": None,
    }
    return render(request, "core/perfil.html", context)
