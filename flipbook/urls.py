# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.views.generic import TemplateView
from flipbook.views import flipbook

urlpatterns = [
    url(r'^$', flipbook, name='flipbook'),
    url(r'^viewer.html$', TemplateView.as_view(template_name="viewer.html", content_type="text/html"), name="viewer") # only relevant when using pdfjs-flipbook
]
