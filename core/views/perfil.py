from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Prefetch

from core.models import Perfil, Produto, Avaliacao, Pedido, PedidoVendedor, ItemPedido
from core.forms import CompleteClientProfileForm, CompletePartnerProfileForm

@login_required
def perfil_detail(request):
    """
    Exibe a página de perfil do usuário logado ou de outro usuário,
    mostrando dados do perfil, dashboard e avaliações dos produtos.
    """

    perfil, created = Perfil.objects.get_or_create(usuario=request.user)
    perfil_usuario = request.user.perfil

   
    if perfil.tipo == 'CLIENTE':
        FormClass = CompleteClientProfileForm
    elif perfil.tipo in ['VENDEDOR', 'ONG']:
        FormClass = CompletePartnerProfileForm  
    else:
        FormClass = None

    form = None
    if FormClass:
        if request.method == 'POST' and 'editar_perfil' in request.POST:
            form = FormClass(request.POST, request.FILES, instance=perfil)
            if form.is_valid():
                form.save()
                messages.success(request, "Perfil atualizado com sucesso!")
                return redirect('core:perfil')
        else:
            form = FormClass(instance=perfil)

    ultimos_pedidos = []

  
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
        produtos_vendedor = Produto.objects.filter(vendedor=perfil).values_list("id", flat=True)

        pedidos_qs = (
            Pedido.objects.filter(sub_pedidos__itens__produto_id__in=produtos_vendedor)
            .distinct()
            .prefetch_related(
                Prefetch(
                    "sub_pedidos",
                    queryset=PedidoVendedor.objects.prefetch_related(
                        Prefetch(
                            "itens",
                            queryset=ItemPedido.objects.filter(produto_id__in=produtos_vendedor).select_related("produto")
                        )
                    ).select_related("vendedor")
                )
            )
            .select_related("cliente")
            .order_by("-data_criacao")
        )
        ultimos_pedidos = pedidos_qs[:5]

 
    dashboard_data = {
        "baixo_estoque": [], 
        "ultimos_pedidos": ultimos_pedidos
    }

 
    avaliacoes_produtos = Avaliacao.objects.none()
    if perfil.tipo == 'VENDEDOR':
        produtos = Produto.objects.filter(vendedor=perfil)
        if produtos.exists():
            produto_content_type = ContentType.objects.get_for_model(Produto)
            avaliacoes_produtos = Avaliacao.objects.filter(
                content_type=produto_content_type,
                object_id__in=produtos.values_list('id', flat=True)
            ).select_related('autor')

            produtos_dict = {p.id: p for p in produtos}
            for avaliacao in avaliacoes_produtos:
                avaliacao.produto = produtos_dict.get(avaliacao.object_id)

    total_avaliacoes = avaliacoes_produtos.count()
    media_avaliacoes = (
        sum(a.nota for a in avaliacoes_produtos) / total_avaliacoes
        if total_avaliacoes > 0 else 0
    )

    context = {
        "perfil": perfil,
        "dashboard": dashboard_data,
        "form": form,
        "user": request.user,
        "avaliacoes_produtos": avaliacoes_produtos,
        "total_avaliacoes": total_avaliacoes,
        "media_avaliacoes": media_avaliacoes,
    }

    return render(request, "core/perfil.html", context)
