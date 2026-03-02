# -*- coding: utf-8 -*-
from django.core.paginator import Paginator
from django.shortcuts import render
from flipbook.models import PdfFlipbook


def flipbook(request):
    document_list = PdfFlipbook.objects.all()
    paginator = Paginator(document_list, 12)
    page_number = request.GET.get('page')
    documents = paginator.get_page(page_number)

    return render(request, 'flipbook/index.html', {'documents': documents})
