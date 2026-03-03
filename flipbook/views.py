# -*- coding: utf-8 -*-
from django.core.paginator import Paginator
from django.shortcuts import render
from flipbook.models import FlipbookCategory, PdfFlipbook


def flipbook(request):
    qs = PdfFlipbook.objects.select_related('category').all()

    categories = FlipbookCategory.objects.all()
    active_category = None
    cat_id = request.GET.get('category')
    if cat_id:
        try:
            active_category = int(cat_id)
            qs = qs.filter(category_id=active_category)
        except (ValueError, TypeError):
            pass

    paginator = Paginator(qs, 12)
    page_number = request.GET.get('page')
    documents = paginator.get_page(page_number)

    return render(request, 'flipbook/index.html', {
        'documents': documents,
        'categories': categories,
        'active_category': active_category,
    })
