# core/views/checkout.py

import json
from decimal import Decimal
from django.utils import timezone
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

        # ============================================================
        # NOVO BLOCO: Atualiza o Perfil do cliente com os valores
        # do formulário de endereço, SOMENTE quando houverem dados
        # (ou seja, quando o checkbox tiver permitido edição).
        # ============================================================
        posted_nome         = request.POST.get("nome", "").strip()
        posted_telefone     = request.POST.get("telefone", "").strip()
        posted_cep          = request.POST.get("cep", "").strip()
        posted_rua          = request.POST.get("rua", "").strip()
        posted_numero       = request.POST.get("numero", "").strip()
        posted_complemento  = request.POST.get("complemento", "").strip()
        posted_bairro       = request.POST.get("bairro", "").strip()
        posted_cidade       = request.POST.get("cidade", "").strip()
        posted_estado       = request.POST.get("estado", "").strip()

        tem_dados_endereco = any([
            posted_nome, posted_telefone, posted_cep, posted_rua, posted_numero,
            posted_complemento, posted_bairro, posted_cidade, posted_estado
        ])

        if tem_dados_endereco:
            campos_atualizados = []

            if posted_nome and hasattr(cliente_perfil, "nome"):
                cliente_perfil.nome = posted_nome
                campos_atualizados.append("nome")

            if posted_telefone and hasattr(cliente_perfil, "telefone"):
                cliente_perfil.telefone = posted_telefone
                campos_atualizados.append("telefone")

            if posted_cep and hasattr(cliente_perfil, "cep"):
                cliente_perfil.cep = posted_cep
                campos_atualizados.append("cep")

            if posted_rua and hasattr(cliente_perfil, "rua"):
                cliente_perfil.rua = posted_rua
                campos_atualizados.append("rua")

            if posted_numero and hasattr(cliente_perfil, "numero"):
                cliente_perfil.numero = posted_numero
                campos_atualizados.append("numero")

            if posted_complemento and hasattr(cliente_perfil, "complemento"):
                cliente_perfil.complemento = posted_complemento
                campos_atualizados.append("complemento")

            if posted_bairro and hasattr(cliente_perfil, "bairro"):
                cliente_perfil.bairro = posted_bairro
                campos_atualizados.append("bairro")

            if posted_cidade and hasattr(cliente_perfil, "cidade"):
                cliente_perfil.cidade = posted_cidade
                campos_atualizados.append("cidade")

            if posted_estado and hasattr(cliente_perfil, "estado"):
                cliente_perfil.estado = posted_estado
                campos_atualizados.append("estado")

            # Se existir 'endereco' agregado no Perfil, mantém coerência textual.
            if hasattr(cliente_perfil, "endereco"):
                partes_logradouro = []
                if posted_rua: partes_logradouro.append(posted_rua)
                if posted_numero: partes_logradouro.append(posted_numero)
                logradouro = ", ".join(partes_logradouro) if partes_logradouro else ""

                partes_localidade = []
                if posted_bairro: partes_localidade.append(posted_bairro)
                if posted_cidade: partes_localidade.append(posted_cidade)
                if posted_estado: partes_localidade.append(posted_estado)
                localidade = ", ".join(partes_localidade) if partes_localidade else ""

                cep_str = posted_cep if posted_cep else ""
                comp_str = posted_complemento if posted_complemento else ""

                endereco_parts = [p for p in [logradouro, localidade, cep_str] if p]
                endereco_str = " - ".join(endereco_parts)
                if comp_str:
                    endereco_str = f"{endereco_str} (Comp.: {comp_str})" if endereco_str else comp_str

                if endereco_str:
                    cliente_perfil.endereco = endereco_str
                    campos_atualizados.append("endereco")

            if campos_atualizados:
                # remove duplicidades e salva apenas campos realmente alterados
                cliente_perfil.save(update_fields=list(set(campos_atualizados)))
        # ============================================================

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