from django.shortcuts import render
from django.http import HttpResponse
from django.urls import path
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    path('', views.quest_home, name='index'),
    path('tests/', views.test_list, name='test_list'),
    path('tests/<int:test_id>/start/', views.start_test, name='start_test'),
    path('tests/result/<int:result_id>/', views.take_test, name='take_test'),
    path('tests/result/<int:result_id>/complete/', views.test_result, name='test_result'),
    path('quests/', views.quest_sequence_list, name='quest_sequence_list'),
    path('quests/sequence/<int:sequence_id>/', views.quest_sequence_detail, name='quest_sequence_detail'),
    path('quests/<int:quest_id>/', views.quest_detail, name='quest_detail'),
    path('quests/<int:quest_id>/start/', views.start_quest_test, name='start_quest_test'),
    path('quests/test/<int:result_id>/', views.take_quest_test, name='take_quest_test'),
    path('quests/test/<int:result_id>/result/', views.quest_test_result, name='quest_test_result'),
    path('quests/<int:quest_id>/guess/', views.guess_code, name='guess_code'),
]

