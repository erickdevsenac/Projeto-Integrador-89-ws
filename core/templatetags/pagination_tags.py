from django import template

register = template.Library()

@register.simple_tag
def query_transform(request, **kwargs):
    """
    Altera os parâmetros de query da URL atual.
    """
    updated = request.GET.copy()
    for k, v in kwargs.items():
        if v is not None:
            updated[k] = v
        else:
            updated.pop(k, 0)
    return updated.urlencode()