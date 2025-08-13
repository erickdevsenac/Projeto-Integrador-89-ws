from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import 
from .forms import ReceitaForm
def cria_receita(request):
    if request.method == 'POST':
        form = ReceitaForm(request.POST, request.FILES)
        if form.is_valid():
            receita = form.save(commit=False)
            receita.pessoa = request.user
            receita.save()
            return redirect('minhas_receitas')
    else:
        form = ReceitaForm()
    return render(request, 'receitas/cria_receita.html', {'form': form})

