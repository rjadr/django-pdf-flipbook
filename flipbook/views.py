# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.template import RequestContext
from flipbook.models import PdfFlipbook

def flipbook(request):
    documents = PdfFlipbook.objects.all()
    print(documents)

    return render(
        request,
        'index.html',
        {'documents': documents}
    )
