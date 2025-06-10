from django.contrib import admin
from .models import (
    Question, Answer, Test, TestResult, QuestionResponse,
    QuestSequence, Quest, QuestProgress, SequenceProgress
)

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

# Register the Quest Sequence models
@admin.register(QuestSequence)
class QuestSequenceAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']

@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = ['title', 'sequence', 'order', 'code', 'created_at']
    list_filter = ['sequence', 'created_at']
    search_fields = ['title', 'description', 'code']
    ordering = ['sequence', 'order']

@admin.register(QuestProgress)
class QuestProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'quest', 'is_completed', 'code_guessed', 'correct_answers', 'total_answers']
    list_filter = ['is_completed', 'code_guessed', 'quest__sequence']
    search_fields = ['student__username', 'quest__title']
    readonly_fields = ['revealed_letters']

@admin.register(SequenceProgress)
class SequenceProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'sequence', 'current_quest', 'is_completed', 'updated_at']
    list_filter = ['is_completed', 'sequence']
    search_fields = ['student__username', 'sequence__title']
    readonly_fields = ['completed_quests']