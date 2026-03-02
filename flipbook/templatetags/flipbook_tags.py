from django import template
from flipbook.models import PdfFlipbook

register = template.Library()


@register.inclusion_tag('flipbook/_collection_grid.html')
def flipbook_collection(collection=None):
    """Render a DearFlip thumbnail grid for a collection (or all PDFs).

    Usage in any Django template::

        {% load flipbook_tags %}

        {# All PDFs #}
        {% flipbook_collection %}

        {# By Wagtail collection pk #}
        {% flipbook_collection 12 %}

        {# By Wagtail collection name #}
        {% flipbook_collection "Annual Reports" %}
    """
    qs = PdfFlipbook.objects.all()

    if collection is not None:
        if isinstance(collection, int) or (isinstance(collection, str) and collection.isdigit()):
            qs = qs.filter(collection_id=int(collection))
        elif isinstance(collection, str):
            qs = qs.filter(collection__name=collection)
        else:
            # Accept a Collection instance directly
            qs = qs.filter(collection=collection)

    return {'documents': qs}
