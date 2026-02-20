import json
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.forms import CheckoutForm
from core.models import (
    Cupom,
    ItemPedido,
    PacoteSurpresa,
    Pedido,
    PedidoVendedor,
    Perfil,
    Produto,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _montar_carrinho(request):
    """
    Constrói o carrinho detalhado a partir da sessão.
    Retorna (carrinho_detalhado, total_carrinho, produtos_db, pacotes_db).
    """
    carrinho_session = request.session.get("carrinho", {})
    if not carrinho_session:
        return [], Decimal("0.00"), {}, {}

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

    for item_key, item_data in carrinho_session.items():
        item_obj = produtos_db.get(item_key) or pacotes_db.get(item_key)
        if not item_obj:
            continue
        quantidade = int(item_data.get("quantidade", 0))
        subtotal = item_obj.preco * quantidade
        total_carrinho += subtotal
        carrinho_detalhado.append(
            {
                "item_key": item_key,
                "nome": item_obj.nome,
                "quantidade": quantidade,
                "preco": item_obj.preco,
                "subtotal": subtotal,
            }
        )

    return carrinho_detalhado, total_carrinho, produtos_db, pacotes_db


def _recuperar_cupom(request, total_base: Decimal):
    """
    Recupera cupom da sessão e calcula desconto.
    Retorna (cupom, valor_desconto, total_final).
    """
    cupom_id = request.session.get("cupom_id")
    cupom = None
    valor_desconto = Decimal("0.00")

    if cupom_id:
        try:
            cupom = Cupom.objects.get(id=cupom_id)
            if cupom.esta_valido:
                valor_desconto = cupom.calcular_desconto(total_base)
            else:
                del request.session["cupom_id"]
                cupom = None
        except Cupom.DoesNotExist:
            request.session.pop("cupom_id", None)
            cupom = None

    total_final = total_base - valor_desconto
    return cupom, valor_desconto, total_final


# ---------------------------------------------------------------------------
# Checkout Page
# ---------------------------------------------------------------------------


@login_required(login_url="/login/")
def checkout_page(request):
    carrinho_session = request.session.get("carrinho", {})
    if not carrinho_session:
        messages.warning(request, "Seu carrinho está vazio para iniciar o checkout.")
        return redirect("core:produtos")

    try:
        perfil = request.user.perfil
    except Perfil.DoesNotExist:
        messages.error(request, "Você precisa completar seu perfil antes de comprar.")
        return redirect("core:perfil")

    carrinho_detalhado, total_carrinho, _, _ = _montar_carrinho(request)

    cupom, valor_desconto, total_final = _recuperar_cupom(request, total_carrinho)

    # Aqui você pode usar apenas endereco completo, ou juntar rua/número/bairro
    form = CheckoutForm(
        initial={
            "endereco_entrega": perfil.endereco,  # campo do seu modelo Perfil
            "forma_pagamento": None,
        }
    )

    context = {
        "form": form,
        "carrinho": carrinho_detalhado,
        "total_carrinho": total_carrinho,
        "total_final": total_final,
        "valor_desconto": valor_desconto,
        "cupom": cupom,
        "usuario": perfil,  # usado pelo template para mostrar resumo de endereço
    }
    return render(request, "core/checkout.html", context)


# ---------------------------------------------------------------------------
# Finalizar Pedido
# ---------------------------------------------------------------------------


@login_required(login_url="/login/")
@transaction.atomic
def finalizar_pedido(request):
    """
    Processa o formulário de checkout e finaliza o pedido.
    """
    if request.method != "POST":
        return redirect("core:checkout_page")

    carrinho_session = request.session.get("carrinho", {})
    if not carrinho_session:
        messages.error(request, "Seu carrinho está vazio.")
        return redirect("core:produtos")

    try:
        cliente_perfil = request.user.perfil
    except Perfil.DoesNotExist:
        messages.error(request, "Perfil de cliente não encontrado.")
        return redirect("core:perfil")

    # Carrinho com travas de estoque
    produto_ids = [
        int(k.split("_")[1]) for k in carrinho_session if k.startswith("produto_")
    ]
    pacote_ids = [
        int(k.split("_")[1]) for k in carrinho_session if k.startswith("pacote_")
    ]

    produtos_db = {
        f"produto_{p.id}": p
        for p in Produto.objects.select_for_update().filter(id__in=produto_ids)
    }
    pacotes_db = {
        f"pacote_{p.id}": p
        for p in PacoteSurpresa.objects.select_for_update().filter(id__in=pacote_ids)
    }

    total_pedido = Decimal("0.00")
    pedidos_por_vendedor = {}

    for item_key, item_data in carrinho_session.items():
        item_obj = produtos_db.get(item_key) or pacotes_db.get(item_key)
        quantidade = item_data["quantidade"]

        if not item_obj or quantidade > item_obj.quantidade_estoque:
            messages.error(
                request,
                f"Estoque insuficiente para "
                f"'{item_obj.nome if item_obj else 'item desconhecido'}'.",
            )
            return redirect("core:ver_carrinho")

        subtotal = item_obj.preco * quantidade
        total_pedido += subtotal

        vendedor = item_obj.vendedor
        if vendedor not in pedidos_por_vendedor:
            pedidos_por_vendedor[vendedor] = {
                "itens": [],
                "subtotal": Decimal("0.00"),
            }

        pedidos_por_vendedor[vendedor]["itens"].append(
            {
                "item_obj": item_obj,
                "quantidade": quantidade,
                "preco_unitario": item_obj.preco,
            }
        )
        pedidos_por_vendedor[vendedor]["subtotal"] += subtotal

    # Cupom
    cupom, valor_desconto, total_final = _recuperar_cupom(request, total_pedido)

    form = CheckoutForm(request.POST)
    if form.is_valid():
        endereco_entrega = form.cleaned_data["endereco_entrega"]
        forma_pagamento = form.cleaned_data["forma_pagamento"]

        # Se quiser, atualize o endereço padrão do perfil com o usado no pedido:
        # cliente_perfil.endereco = endereco_entrega
        # cliente_perfil.save(update_fields=["endereco"])

        pedido_principal = Pedido.objects.create(
            cliente=cliente_perfil,
            valor_produtos=total_pedido,
            endereco_entrega=endereco_entrega,
            forma_pagamento=forma_pagamento,
            cupom_aplicado=cupom,
            valor_desconto=valor_desconto,
            # valor_total calculado no save() do modelo
        )

        if cupom:
            cupom.usar_cupom()

        for vendedor, dados in pedidos_por_vendedor.items():
            sub_pedido = PedidoVendedor.objects.create(
                pedido_principal=pedido_principal,
                vendedor=vendedor,
                valor_subtotal=dados["subtotal"],
            )
            for item in dados["itens"]:
                item_obj = item["item_obj"]

                item_pedido_dados = {
                    "sub_pedido": sub_pedido,
                    "quantidade": item["quantidade"],
                    "preco_unitario": item["preco_unitario"],
                }
                if isinstance(item_obj, Produto):
                    item_pedido_dados["produto"] = item_obj
                elif isinstance(item_obj, PacoteSurpresa):
                    item_pedido_dados["pacote_surpresa"] = item_obj

                ItemPedido.objects.create(**item_pedido_dados)

                # Atualiza estoque
                item_obj.quantidade_estoque -= item["quantidade"]
                item_obj.save()

        # Limpa sessão
        request.session.pop("carrinho", None)
        request.session.pop("cupom_id", None)

        messages.success(
            request,
            f"Pedido #{pedido_principal.numero_pedido} finalizado com sucesso!",
        )
        return redirect("core:meus_pedidos")

    # Form inválido: re-renderiza checkout com erros
    carrinho_detalhado, total_carrinho, _, _ = _montar_carrinho(request)
    perfil = cliente_perfil

    context = {
        "form": form,
        "carrinho": carrinho_detalhado,
        "total_carrinho": total_pedido,
        "total_final": total_final,
        "valor_desconto": valor_desconto,
        "cupom": cupom,
        "usuario": perfil,
    }
    return render(request, "core/checkout.html", context)


# ---------------------------------------------------------------------------
# Cupom APIs (mantidos)
# ---------------------------------------------------------------------------


@require_POST
def api_aplicar_cupom(request):
    """
    Endpoint da API para aplicar um cupom de desconto via AJAX.
    """
    try:
        data = json.loads(request.body)
        codigo = data.get("codigo", "").strip()

        carrinho_session = request.session.get("carrinho", {})
        if not carrinho_session:
            return JsonResponse(
                {"success": False, "mensagem": "Seu carrinho está vazio."},
                status=400,
            )

        produto_ids = [int(pid) for pid in carrinho_session.keys()]
        produtos_map = {
            str(p.id): p for p in Produto.objects.filter(id__in=produto_ids)
        }
        total_carrinho = sum(
            produtos_map[pid].preco * item_data["quantidade"]
            for pid, item_data in carrinho_session.items()
            if pid in produtos_map
        )
        total_carrinho = Decimal(total_carrinho)

        cupom = Cupom.objects.get(codigo__iexact=codigo)

        if not cupom.esta_valido:
            return JsonResponse(
                {"success": False, "mensagem": "Este cupom não é mais válido."},
                status=400,
            )

        valor_desconto = cupom.calcular_desconto(total_carrinho)

        if valor_desconto <= 0:
            msg = (
                "O valor mínimo da compra para este cupom é de "
                f"R$ {cupom.valor_minimo_compra:.2f}."
            )
            return JsonResponse({"success": False, "mensagem": msg}, status=400)

        total_final = total_carrinho - valor_desconto
        request.session["cupom_id"] = cupom.id

        return JsonResponse(
            {
                "success": True,
                "mensagem": f"Cupom '{cupom.codigo}' aplicado!",
                "cupom": {
                    "codigo": cupom.codigo,
                    "desconto": str(cupom),
                },
                "valores": {
                    "valor_desconto_str": f"− R$ {valor_desconto:.2f}".replace(
                        ".", ","
                    ),
                    "total_final_str": f"R$ {total_final:.2f}".replace(".", ","),
                },
            }
        )

    except Cupom.DoesNotExist:
        request.session.pop("cupom_id", None)
        return JsonResponse(
            {"success": False, "mensagem": "Cupom inválido."}, status=404
        )
    except Exception:
        return JsonResponse(
            {"success": False, "mensagem": "Ocorreu um erro inesperado."}, status=500
        )


def aplicar_cupom(request):
    """
    Aplica cupom com recarregamento da página (fallback).
    """
    if request.method == "POST":
        codigo = request.POST.get("codigo", "").strip()
        try:
            cupom = Cupom.objects.get(codigo__iexact=codigo)
            if cupom.esta_valido:
                request.session["cupom_id"] = cupom.id
                messages.success(
                    request, f"Cupom '{cupom.codigo}' aplicado com sucesso!"
                )
            else:
                messages.error(request, "Cupom inválido ou expirado.")
        except Cupom.DoesNotExist:
            request.session.pop("cupom_id", None)
            messages.error(request, "Cupom inválido ou expirado.")
    return redirect("core:checkout_page")


@login_required(login_url="/login/")
def meus_pedidos(request):
    """
    Lista os pedidos do usuário logado (cliente ou vendedor).
    """
    perfil_usuario = request.user.perfil

    ultimos_pedidos = Pedido.objects.none()
    pedidos_qs = Pedido.objects.none()

    if perfil_usuario.tipo in [Perfil.TipoUsuario.CLIENTE, "ONG"]:
        pedidos_qs = (
            Pedido.objects.filter(cliente=perfil_usuario)
            .prefetch_related(
                Prefetch(
                    "sub_pedidos",
                    queryset=PedidoVendedor.objects.select_related("vendedor"),
                ),
                Prefetch(
                    "sub_pedidos__itens",
                    queryset=ItemPedido.objects.select_related("produto"),
                ),
            )
            .order_by("-data_criacao")
        )
        ultimos_pedidos = pedidos_qs[:5]

    elif perfil_usuario.tipo == Perfil.TipoUsuario.VENDEDOR:
        pedidos_qs = (
            PedidoVendedor.objects.filter(vendedor=perfil_usuario)
            .select_related("pedido_principal", "vendedor")
            .prefetch_related("itens__produto")
            .order_by("-pedido_principal__data_criacao")
        )
        ultimos_pedidos = pedidos_qs[:5]

    paginator = Paginator(pedidos_qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "ultimos_pedidos": ultimos_pedidos,
        "tipo_usuario": perfil_usuario.tipo,
    }
    return render(request, "core/meus_pedidos.html", context)


@login_required
def painel_pedidos_vendedor(request):
    """
    Painel específico para vendedores verem seus pedidos.
    """
    vendedor = request.user.perfil

    if vendedor.tipo != Perfil.TipoUsuario.VENDEDOR:
        return redirect("core:perfil")

    hoje = timezone.now().date()

    pedidos_hoje = (
        PedidoVendedor.objects.filter(
            vendedor=vendedor, pedido_principal__data_criacao__date=hoje
        )
        .select_related("pedido_principal", "vendedor")
        .prefetch_related("itens__produto", "itens__pacote_surpresa")
    )

    pedidos_anteriores = (
        PedidoVendedor.objects.filter(vendedor=vendedor)
        .exclude(pedido_principal__data_criacao__date=hoje)
        .select_related("pedido_principal", "vendedor")
        .prefetch_related("itens__produto", "itens__pacote_surpresa")
    )

    context = {
        "pedidos_hoje": pedidos_hoje,
        "pedidos_anteriores": pedidos_anteriores,
    }

    return render(request, "core/painel_pedidos_vendedor.html", context)
