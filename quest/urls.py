from django.shortcuts import render
from django.http import HttpResponse
from django.urls import path
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='/tests/', permanent=True), name='index'),
    path('tests/', views.test_list, name='test_list'),
    path('tests/<int:test_id>/start/', views.start_test, name='start_test'),
    path('tests/result/<int:result_id>/', views.take_test, name='take_test'),
    path('tests/result/<int:result_id>/complete/', views.test_result, name='test_result'),
]

