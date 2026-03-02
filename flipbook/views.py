# -*- coding: utf-8 -*-
from django.apps import apps
from django.core.paginator import Paginator
from django.shortcuts import render
from flipbook.models import PdfFlipbook

_wagtail = apps.is_installed('wagtail')


def flipbook(request):
    qs = PdfFlipbook.objects.all()

    # Optional collection filter (Wagtail only)
    collections = None
    active_collection = None
    if _wagtail:
        from wagtail.models import Collection
        collections = Collection.objects.order_by('name')
        col_id = request.GET.get('collection')
        if col_id:
            try:
                active_collection = int(col_id)
                qs = qs.filter(collection_id=active_collection)
            except (ValueError, TypeError):
                pass

    paginator = Paginator(qs, 12)
    page_number = request.GET.get('page')
    documents = paginator.get_page(page_number)

    return render(request, 'flipbook/index.html', {
        'documents': documents,
        'collections': collections,
        'active_collection': active_collection,
    })
