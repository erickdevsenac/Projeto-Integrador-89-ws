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

def vendedor(request):
    return render(request,"core/vendedor.html")
