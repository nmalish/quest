from django.shortcuts import render
from django.http import HttpResponse
from django.urls import path
from . import views

urlpatterns = [
    path('tests/', views.test_list, name='test_list'),
    path('tests/<int:test_id>/start/', views.start_test, name='start_test'),
    path('tests/result/<int:result_id>/', views.take_test, name='take_test'),
    path('tests/result/<int:result_id>/complete/', views.test_result, name='test_result'),
]

