from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from core.models import Avaliacao
from core.forms import AvaliacaoForm

def avaliacao(request):
    avaliacoes = Avaliacao.objects.all().order_by('-data_criacao')
    paginator = Paginator(avaliacoes, 10)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'core/avaliacao.html', {'page_obj': page})

@login_required
def nova_avaliacao(request):
    form = AvaliacaoForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            nova = form.save(commit=False)
            nova.autor = request.user
            nova.save()
            messages.success(request, "Avaliação enviada com sucesso!")
            return redirect("core:avaliacao")
        messages.error(request, "Erro ao enviar avaliação.")
    return render(request, "core/nova_avaliacao.html", {"form": form})
