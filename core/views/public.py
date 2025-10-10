from django.shortcuts import render, get_object_or_404
from core.models import Perfil, EquipeDev

def index(request):
    return render(request, 'core/index.html')

def ongs_pagina(request, usuario_id):
    ong = get_object_or_404(Perfil, tipo="ONG", usuario_id=usuario_id)
    return render(request, 'core/ong_pagina.html', {"inf_ongs": ong})

def contato(request):
    return render(request, "core/contato.html")

def devs(request):
    equipe = EquipeDev.objects.all()
    return render(request, "core/timedev.html", {"equipe": equipe})

def doacao(request):
    ongs = Perfil.objects.filter(tipo="ONG")
    return render(request, "core/doacao.html", {"instituicoes": ongs})

def videos(request):
    return render(request, "core/videos.html")

def notificacao(request):
    return render(request,"core/notificacoes.html")

def vendedor(request, usuario_id):
    """
    Exibe a página de perfil público de um vendedor específico.
    """
    vendedor_perfil = get_object_or_404(
        Perfil, 
        usuario_id=usuario_id, 
        tipo=Perfil.TipoUsuario.VENDEDOR
    )

    produtos_vendedor = vendedor_perfil.produtos.filter(ativo=True)

    context = {
        'vendedor': vendedor_perfil,
        'produtos': produtos_vendedor,
    }
    
    return render(request, "core/vendedor.html", context)
