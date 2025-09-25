from core.models import Categoria

def global_settings(request):
    """
    Esse context processor adiciona variáveis globais disponíveis em todos os templates.
    """
    return {
        "project_name": "Projeto Integrador 89",
        "version": "1.0.0",
        "author": "Equipe SENAC"
    }

def carrinho_context(request):
    """
    Adiciona informações do carrinho de compras no contexto de todos os templates.
    """
    carrinho = request.session.get("carrinho", {})

    # Exemplo: total de itens
    total_itens = sum(item.get("quantidade", 0) for item in carrinho.values())

    # Exemplo: valor total
    valor_total = sum(
        float(item.get("quantidade", 0)) * float(item.get("preco", 0)) for item in carrinho.values()
    )

    return {
        "carrinho": carrinho,
        "total_itens": total_itens,
        "valor_total": valor_total,
    }

def categorias_context(request):
    """
    Deixa as categorias disponíveis em todos os templates.
    """
    categorias = Categoria.objects.all()
    return {"categorias": categorias}