# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 23:26:34 2018

@author: Sam Chen
"""

from django.urls import path

from . import views

urlpatterns = [
        path('', views.index, name='index'),
        path('results/', views.results, name='results'),
        path('results/download/', views.download_inExcel, name='download_inExcel'),
        path('dataset/<int:dataset_id>/', views.dataset_info, name='dataset_info'),
        path('processing/', views.processing, name='processing'),
        path('documentation/', views.documentation, name='documentation'),
        path('search/', views.search, name='search')
        ]