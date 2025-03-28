from django.contrib import admin
from .models import Question, Answer, Test, TestResult, QuestionResponse

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'question_type')
    search_fields = ('description',)
    list_filter = ('question_type',)

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')
    list_filter = ('is_correct', 'question')
    search_fields = ('text', 'question__description')

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'time_limit')
    search_fields = ('title', 'description')
    filter_horizontal = ('questions',)

@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'test', 'status', 'started_at', 'completed_at', 'score')
    list_filter = ('status', 'test', 'student')
    search_fields = ('student__username', 'test__title')
    readonly_fields = ('started_at', 'completed_at')

@admin.register(QuestionResponse)
class QuestionResponseAdmin(admin.ModelAdmin):
    list_display = ('test_result', 'question', 'is_correct', 'submitted_at')
    list_filter = ('is_correct', 'test_result__test', 'test_result__student')
    search_fields = ('test_result__student__username', 'question__description')
    readonly_fields = ('submitted_at',)