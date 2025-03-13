from django.contrib import admin
from .models import Question, Answer

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 3

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('description', 'type')
    inlines = [AnswerInline]

admin.site.register(Question, QuestionAdmin)