from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from core.models import Receita, Dica
from core.forms import ReceitaForm, IngredienteFormSet, EtapaPreparoFormSet

def receitas(request):
    lista_receitas = Receita.objects.filter(disponivel=True).order_by('-data_criacao')
    paginator = Paginator(lista_receitas, 9)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'core/receitas.html', {'page_obj': page_obj})

def receita_detalhe(request, receita_id):
    receita = get_object_or_404(Receita, id=receita_id, disponivel=True)
    return render(request, 'core/receita_detalhe.html', {'receita': receita})

def dicas(request):
    lista_dicas = Dica.objects.filter(publicada=True).order_by('-data_publicacao')
    return render(request, "core/dicas.html", {"dicas": lista_dicas})

@login_required
def cria_receita(request):
    if request.method == "POST":
        form = ReceitaForm(request.POST, request.FILES)
        ingrediente_formset = IngredienteFormSet(request.POST, prefix="ingredientes")
        etapa_formset = EtapaPreparoFormSet(request.POST, prefix="etapas")
        
        if form.is_valid() and ingrediente_formset.is_valid() and etapa_formset.is_valid():
            receita = form.save(commit=False)
            receita.autor = request.user
            receita.save()
            ingrediente_formset.instance = receita
            ingrediente_formset.save()
            etapa_formset.instance = receita
            etapa_formset.save()
            messages.success(request, f"Receita '{receita.titulo}' criada com sucesso!")
            return redirect("core:receitas")
        else:
            messages.error(request, "Erro ao criar receita. Verifique os campos.")
    else:
        form = ReceitaForm()
        ingrediente_formset = IngredienteFormSet(prefix="ingredientes")
        etapa_formset = EtapaPreparoFormSet(prefix="etapas")
        
    context = {
        "form": form,
        "ingrediente_formset": ingrediente_formset,
        "etapa_formset": etapa_formset,
    }
    return render(request, "core/cria_receita.html", context)