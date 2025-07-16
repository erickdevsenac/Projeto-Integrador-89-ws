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
def telalogin(request):
    return render(request,"core/telalogin.html")

def receitas(request):
    return render (request, 'core/receitas.html')

def videos(request):
    return render (request, 'core/videos.html')