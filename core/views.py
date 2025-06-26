from django.shortcuts import render

def index(request):
    return render(request, 'core/index.html')

def header(request):
    return render(request, 'core/header.html')