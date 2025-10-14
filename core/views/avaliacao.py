from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from core.forms import AvaliacaoForm
from core.models import Avaliacao


def avaliacao(request):
    avaliacoes = Avaliacao.objects.all().order_by("-data_criacao")
    paginator = Paginator(avaliacoes, 10)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "core/avaliacao.html", {"page_obj": page})


@login_required
@login_required
def nova_avaliacao(request, object_pk, model_name):
    try:
        RatedModel = apps.get_model("core", model_name)
    except LookupError:
        messages.error(request, "Modelo para avaliação não encontrado.")
        return redirect("core:avaliacao")

    rated_object = get_object_or_404(RatedModel, pk=object_pk)

    form = AvaliacaoForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            nova = form.save(commit=False)

            nova.autor = request.user
            nova.object_id = rated_object.pk
            nova.content_type = ContentType.objects.get_for_model(RatedModel)

            nova.save()

            messages.success(
                request, f"Avaliação enviada com sucesso para {rated_object}!"
            )
            return redirect("core:avaliacao")

        messages.error(request, "Erro ao enviar avaliação.")

    # Pass the object to the template context if needed for display
    return render(
        request,
        "core/nova_avaliacao.html",
        {"form": form, "rated_object": rated_object},
    )
