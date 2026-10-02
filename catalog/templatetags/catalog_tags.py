from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Return encoded URL parameters, merging the current GET parameters
    with the new keyword arguments provided.
    If a keyword argument value is None or empty string '', it will be removed.
    """
    request = context.get("request")
    if not request:
        return ""
    d = request.GET.copy()
    for k, v in kwargs.items():
        if v is not None and v != "":
            d[k] = str(v)
        elif k in d:
            del d[k]
    return d.urlencode()

@register.simple_tag(takes_context=True)
def param_remove(context, *keys):
    """
    Return encoded URL parameters removing the given keys.
    """
    request = context.get("request")
    if not request:
        return ""
    d = request.GET.copy()
    for k in keys:
        if k in d:
            del d[k]
    return d.urlencode()

@register.filter
def elided_page_range(page_obj, on_each_side=1, on_ends=1):
    """
    Returns an elided page range (with '…' strings for gaps)
    for clean pagination rendering.
    """
    if not page_obj or not hasattr(page_obj, "paginator"):
        return []
    try:
        return page_obj.paginator.get_elided_page_range(
            number=page_obj.number,
            on_each_side=int(on_each_side),
            on_ends=int(on_ends),
        )
    except Exception:
        return page_obj.paginator.page_range
