from django.shortcuts import get_object_or_404, render,redirect

from core.models import EquipeDev, PacoteSurpresa, Perfil


def index(request):
    context = PacoteSurpresa.objects.filter(ativo=True).order_by("-id")[:8]
    pacotes_surpresa = {"pacotes_surpresa": context}
    return render(request, "core/index.html", pacotes_surpresa)


def ongs_pagina(request, usuario_id):
    ong = get_object_or_404(Perfil, tipo="ONG", usuario_id=usuario_id)
    return render(request, "core/ong_pagina.html", {"inf_ongs": ong})


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
    return render(request, "core/notificacoes.html")


def vendedor(request, usuario_id):
    """
    Exibe a página de perfil público de um vendedor específico.
    """
    vendedor_perfil = get_object_or_404(
        Perfil, usuario_id=usuario_id, tipo=Perfil.TipoUsuario.VENDEDOR
    )

    produtos_vendedor = vendedor_perfil.produtos.filter(ativo=True)
    pacote_detalhe = PacoteSurpresa.objects.all()
    print(pacote_detalhe)

    context = {
        "vendedor": vendedor_perfil,
        "produtos": produtos_vendedor,
        "pacotes": pacote_detalhe,

    }

    return render(request, "core/vendedor.html", context)


def pacote_detalhe(request, pacote_id):
    """
    Exibe a página de detalhes para um Pacote Surpresa específico.
    """
    pacote = get_object_or_404(
        PacoteSurpresa.objects.select_related("vendedor"), id=pacote_id, ativo=True
    )
    context = {"pacote": pacote}
    return render(request, "core/pacote_detalhe.html", context)
def pacote_novo(request):
 
    if request.method == 'POST':
        pacote = PacoteSurpresa.objects.create(
            nome="Novo Pacote",
            descricao="Descrição do pacote",
            preco=10.00,  # Preço de exemplo
            vendedor=request.user,  # Exemplo de vendedor
        )
        return redirect('core:pacote_detalhe', pacote_id=pacote.id)  
    return render(request, "core/pacote.html")