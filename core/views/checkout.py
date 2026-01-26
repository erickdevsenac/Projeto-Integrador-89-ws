# core/views/checkout.py

import json
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import redirect, render
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


@login_required(login_url="/login/")
def checkout_page(request):
    carrinho_session = request.session.get("carrinho", {})
    if not carrinho_session:
        messages.warning(request, "Seu carrinho está vazio para iniciar o checkout.")
        return redirect("core:produtos")

    # Lógica de separação e busca (idêntica a 'ver_carrinho')
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
        if item_obj:
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

    cupom_id = request.session.get("cupom_id")
    cupom = None
    valor_desconto = Decimal("0.00")

    if cupom_id:
        try:
            cupom = Cupom.objects.get(id=cupom_id)
            if cupom.esta_valido:
                valor_desconto = cupom.calcular_desconto(total_carrinho)
            else:
                # Remove cupom inválido da sessão
                del request.session["cupom_id"]
        except Cupom.DoesNotExist:
            del request.session["cupom_id"]

    total_final = total_carrinho - valor_desconto
    form = CheckoutForm(initial={"endereco_entrega": request.user.perfil.endereco})

    context = {
        "form": form,
        "carrinho": carrinho_detalhado,
        "total_carrinho": total_carrinho,
        "total_final": total_final,
        "valor_desconto": valor_desconto,
        "cupom": cupom,
    }
    return render(request, "core/checkout.html", context)


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
                f"Estoque insuficiente para '{item_obj.nome if item_obj else 'item desconhecido'}'.",
            )
            return redirect("core:ver_carrinho")

        subtotal = item_obj.preco * quantidade
        total_pedido += subtotal

        vendedor = item_obj.vendedor
        if vendedor not in pedidos_por_vendedor:
            pedidos_por_vendedor[vendedor] = {"itens": [], "subtotal": Decimal("0.00")}

        pedidos_por_vendedor[vendedor]["itens"].append(
            {
                "item_obj": item_obj,  # Passa o objeto inteiro
                "quantidade": quantidade,
                "preco_unitario": item_obj.preco,
            }
        )
        pedidos_por_vendedor[vendedor]["subtotal"] += subtotal

    # Validação e cálculo do cupom
    cupom_id = request.session.get("cupom_id")
    cupom = None
    valor_desconto = Decimal("0.00")

    if cupom_id:
        try:
            cupom = Cupom.objects.get(id=cupom_id)
            if cupom.esta_valido:
                valor_desconto = cupom.calcular_desconto(total_pedido)
            else:
                messages.error(
                    request, "O cupom em sua sessão expirou ou não é mais válido."
                )
                del request.session["cupom_id"]
                return redirect("core:checkout_page")
        except Cupom.DoesNotExist:
            del request.session["cupom_id"]

    form = CheckoutForm(request.POST)
    if form.is_valid():
        pedido_principal = Pedido.objects.create(
            cliente=cliente_perfil,
            valor_produtos=total_pedido,
            endereco_entrega=form.cleaned_data["endereco_entrega"],
            forma_pagamento=form.cleaned_data["forma_pagamento"],
            cupom_aplicado=cupom,
            valor_desconto=valor_desconto,
            # O valor_total é calculado automaticamente pelo método save() do modelo Pedido
        )

        if cupom:
            cupom.usar_cupom()  # Incrementa o contador de uso do cupom

        for vendedor, dados in pedidos_por_vendedor.items():
            sub_pedido = PedidoVendedor.objects.create(
                pedido_principal=pedido_principal,
                vendedor=vendedor,
                valor_subtotal=dados["subtotal"],
            )
            for item in dados["itens"]:
                item_obj = item["item_obj"]

                # LÓGICA CRÍTICA DE CRIAÇÃO DO ItemPedido
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

                # Deduzir estoque do objeto correto
                item_obj.quantidade_estoque -= item["quantidade"]
                item_obj.save()

        # Limpa a sessão
        del request.session["carrinho"]
        if "cupom_id" in request.session:
            del request.session["cupom_id"]

        messages.success(
            request, f"Pedido #{pedido_principal.numero_pedido} finalizado com sucesso!"
        )
        return redirect("core:meus_pedidos")
    else:
        # Se o formulário for inválido, renderiza a página novamente com os erros
        # Recarregando o contexto para exibir os erros do formulário
        return render(
            request,
            "core/checkout.html",
            {
                "form": form,
                "carrinho": carrinho_session,
                "total_carrinho": total_pedido,
            },
        )


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
                {"success": False, "mensagem": "Seu carrinho está vazio."}, status=400
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
            msg = f"O valor mínimo da compra para este cupom é de R$ {cupom.valor_minimo_compra:.2f}."
            return JsonResponse({"success": False, "mensagem": msg}, status=400)

        total_final = total_carrinho - valor_desconto
        request.session["cupom_id"] = cupom.id

        return JsonResponse(
            {
                "success": True,
                "mensagem": f"Cupom '{cupom.codigo}' aplicado!",
                "cupom": {
                    "codigo": cupom.codigo,
                    "desconto": str(cupom),  # Usa o __str__ do modelo
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
    perfil_usuario = request.user.perfil

    ultimos_pedidos = Pedido.objects.none()
    pedidos_qs = Pedido.objects.none()

    if perfil_usuario.tipo in [Perfil.TipoUsuario.CLIENTE, 'ONG']:
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
       
        produtos_vendedor = perfil_usuario.produtos.values_list('id', flat=True)

       
        pedidos_qs = (
            Pedido.objects.filter(
                sub_pedidos__itens__produto_id__in=produtos_vendedor
            )
            .distinct()
            .prefetch_related(
                Prefetch(
                    "sub_pedidos",
                    queryset=PedidoVendedor.objects.prefetch_related(
                        Prefetch(
                            "itens",
                            queryset=ItemPedido.objects.filter(
                                produto_id__in=produtos_vendedor
                            ).select_related("produto")
                        )
                    ).select_related("vendedor")
                )
            )
            .select_related("cliente")
            .order_by("-data_criacao")
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