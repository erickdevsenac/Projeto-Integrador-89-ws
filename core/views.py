from django.shortcuts import render

def index(request):
    return render(request, 'core/index.html')

def produtos(request):
    return render(request, 'core/produtos.html')

def contato(request):
    return render(request, 'core/contato.html')

def cadastro(request):
    return render(request, 'core/cadastro.html')

def trocasenha(request):
    return render(request, 'core/senha_erica.html')