import json
from decimal import Decimal

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from core.models import PacoteSurpresa, Produto

@login_required
def ver_carrinho(request):
    """View otimizada para visualização do carrinho com limpeza automática de itens inválidos."""
    carrinho_session = request.session.get("carrinho", {})

    if not carrinho_session:
        return render(
            request,
            "core/carrinho.html",
            {"carrinho": [], "total_carrinho": Decimal("0.00")},
        )

    produto_ids = [
        int(k.split("_")[1]) for k in carrinho_session if k.startswith("produto_")
    ]
    pacote_ids = [
        int(k.split("_")[1]) for k in carrinho_session if k.startswith("pacote_")
    ]

    produtos_db = {
        f"produto_{p.id}": p for p in Produto.objects.filter(id__in=produto_ids)
    }
    pacotes_db = {
        f"pacote_{p.id}": p for p in PacoteSurpresa.objects.filter(id__in=pacote_ids)
    }

    carrinho_detalhado = []
    total_carrinho = Decimal("0.00")

    itens_para_remover = []

    for item_key, item_info in list(carrinho_session.items()):
        item_obj = produtos_db.get(item_key) or pacotes_db.get(item_key)

        if not item_obj or item_obj.quantidade_estoque <= 0:
            itens_para_remover.append(item_key)
            continue

        quantidade = item_info["quantidade"]
        if quantidade > item_obj.quantidade_estoque:
            carrinho_session[item_key]["quantidade"] = item_obj.quantidade_estoque
            quantidade = item_obj.quantidade_estoque

        subtotal = item_obj.preco * quantidade
        total_carrinho += subtotal

        carrinho_detalhado.append(
            {
                "item_key": item_key,
                "item_obj": item_obj,
                "quantidade": quantidade,
                "subtotal": subtotal,
            }
        )

    if itens_para_remover:
        for item_key in itens_para_remover:
            if item_key in carrinho_session:
                del carrinho_session[item_key]

        request.session["carrinho"] = carrinho_session
        messages.warning(
            request,
            "Alguns itens foram removidos do seu carrinho pois não estão mais disponíveis.",
        )

    return render(
        request,
        "core/carrinho.html",
        {"carrinho": carrinho_detalhado, "total_carrinho": total_carrinho},
    )


@require_POST
def adicionar_carrinho(request, produto_id):
    """View para adicionar produtos ao carrinho"""
    produto = get_object_or_404(Produto, id=produto_id, ativo=True)
    carrinho = request.session.get("carrinho", {})

    try:
        quantidade_solicitada = int(request.POST.get("quantidade", 1))
        if quantidade_solicitada <= 0:
            raise ValueError
    except ValueError:
        messages.error(request, "Quantidade inválida.")
        return redirect(request.META.get("HTTP_REFERER", "core:produtos"))

    produto_id_str = f"produto_{produto.id}"
    quantidade_existente = carrinho.get(produto_id_str, {}).get("quantidade", 0)

    if (quantidade_existente + quantidade_solicitada) > produto.quantidade_estoque:
        messages.error(
            request,
            f"Estoque insuficiente. Disponível: {produto.quantidade_estoque} unidades.",
        )
        return redirect(request.META.get("HTTP_REFERER", "core:produtos"))

    carrinho[produto_id_str] = {
        "quantidade": quantidade_existente + quantidade_solicitada,
        "preco": str(produto.preco),
        "nome": produto.nome,
    }

    request.session["carrinho"] = carrinho
    messages.success(request, f"{produto.nome} adicionado ao carrinho.")
    return redirect("core:ver_carrinho")


@require_POST
def adicionar_pacote_carrinho(request, pacote_id):
    """View para adicionar Pacotes Surpresa ao carrinho"""
    pacote = get_object_or_404(PacoteSurpresa, id=pacote_id, ativo=True)
    carrinho = request.session.get("carrinho", {})

    try:
        quantidade_solicitada = int(request.POST.get("quantidade", 1))
        if quantidade_solicitada <= 0:
            raise ValueError
    except ValueError:
        messages.error(request, "Quantidade inválida.")
        return redirect(request.META.get("HTTP_REFERER", "core:index"))

    # Lógica central: usar o prefixo 'pacote_'
    pacote_id_str = f"pacote_{pacote.id}"
    quantidade_existente = carrinho.get(pacote_id_str, {}).get("quantidade", 0)

    if (quantidade_existente + quantidade_solicitada) > pacote.quantidade_estoque:
        messages.error(
            request,
            f"Estoque insuficiente. Disponível: {pacote.quantidade_estoque} pacotes.",
        )
        return redirect(request.META.get("HTTP_REFERER", "core:index"))

    carrinho[pacote_id_str] = {
        "quantidade": quantidade_existente + quantidade_solicitada,
        "preco": str(pacote.preco),
        "nome": pacote.nome,
    }

    request.session["carrinho"] = carrinho
    messages.success(request, f"{pacote.nome} adicionado ao carrinho.")
    return redirect("core:ver_carrinho")


@require_POST
def atualizar_carrinho(request):
    """
    Atualiza a quantidade de um item no carrinho (produtos ou pacotes).
    Responde a requisições AJAX com JSON.
    """
    try:
        data = json.loads(request.body)
        item_key = str(data.get("item_key"))
        quantidade = int(data.get("quantidade", 0))
    except (json.JSONDecodeError, ValueError):
        return JsonResponse(
            {"success": False, "message": "Dados inválidos."}, status=400
        )

    carrinho = request.session.get("carrinho", {})

    if item_key not in carrinho:
        return JsonResponse(
            {"success": False, "message": "Item não encontrado no carrinho."},
            status=404,
        )

    try:
        if item_key.startswith("produto_"):
            item_id = int(item_key.split("_")[1])
            item_obj = Produto.objects.get(id=item_id)
        elif item_key.startswith("pacote_"):
            item_id = int(item_key.split("_")[1])
            item_obj = PacoteSurpresa.objects.get(id=item_id)
        else:
            raise ValueError("Chave de item inválida")

        if quantidade > 0 and quantidade <= item_obj.quantidade_estoque:
            carrinho[item_key]["quantidade"] = quantidade
            request.session["carrinho"] = carrinho

            subtotal = item_obj.preco * quantidade
            total_carrinho = sum(
                Decimal(item["preco"]) * item["quantidade"]
                for item in carrinho.values()
            )
            total_itens = sum(item["quantidade"] for item in carrinho.values())

            return JsonResponse(
                {
                    "success": True,
                    "subtotal": f"R$ {subtotal:,.2f}".replace(",", "X")
                    .replace(".", ",")
                    .replace("X", "."),
                    "total_carrinho": f"R$ {total_carrinho:,.2f}".replace(",", "X")
                    .replace(".", ",")
                    .replace("X", "."),
                    "total_itens": total_itens,
                }
            )
        elif quantidade > item_obj.quantidade_estoque:
            # Se a quantidade for maior que o estoque, ajusta para o máximo disponível
            carrinho[item_key]["quantidade"] = item_obj.quantidade_estoque
            request.session["carrinho"] = carrinho
            return JsonResponse(
                {
                    "success": False,
                    "message": f"Estoque insuficiente. A quantidade foi ajustada para o máximo disponível: {item_obj.quantidade_estoque}",
                },
                status=400,
            )
        else:  # quantidade <= 0
            del carrinho[item_key]
            request.session["carrinho"] = carrinho
            total_carrinho = sum(
                Decimal(item["preco"]) * item["quantidade"]
                for item in carrinho.values()
            )
            total_itens = sum(item["quantidade"] for item in carrinho.values())
            return JsonResponse(
                {
                    "success": True,
                    "removed": True,
                    "total_carrinho": f"R$ {total_carrinho:,.2f}".replace(",", "X")
                    .replace(".", ",")
                    .replace("X", "."),
                    "total_itens": total_itens,
                }
            )

    except (Produto.DoesNotExist, PacoteSurpresa.DoesNotExist):
        return JsonResponse(
            {"success": False, "message": "O item não existe mais."}, status=404
        )
    except ValueError:
        return JsonResponse(
            {"success": False, "message": "Chave de item inválida."}, status=400
        )


@require_POST
def remover_item_carrinho(request):
    """
    Remove um item do carrinho (produtos ou pacotes).
    Responde a requisições AJAX com JSON.
    """
    try:
        data = json.loads(request.body)
        # CORREÇÃO: Ler 'item_key'
        item_key = str(data.get("item_key"))
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "message": "Dados inválidos."}, status=400
        )

    carrinho = request.session.get("carrinho", {})

    if item_key in carrinho:
        del carrinho[item_key]
        request.session["carrinho"] = carrinho

        # Recalcula totais para retornar na resposta
        total_carrinho = sum(
            Decimal(item["preco"]) * item["quantidade"] for item in carrinho.values()
        )
        total_itens = sum(item["quantidade"] for item in carrinho.values())

        return JsonResponse(
            {
                "success": True,
                "message": "Item removido com sucesso.",
                "total_carrinho": f"R$ {total_carrinho:,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                "total_itens": total_itens,
            }
        )

    return JsonResponse(
        {"success": False, "message": "Item não encontrado no carrinho."}, status=404
    )
