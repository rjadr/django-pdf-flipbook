# -*- coding: utf-8 -*-
from django.urls import path
from flipbook.views import flipbook

urlpatterns = [
    path('', flipbook, name='flipbook'),
]
