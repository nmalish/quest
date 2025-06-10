from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

# Create your models here.
from django.contrib.auth.models import User  # built-in User model for later use

class Question(models.Model):
    description = models.TextField()  # question text
    image = models.ImageField(upload_to='questions/', blank=True, null=True)  # optional image
    QUESTION_TYPES = [
        ('MC', 'Multiple Choice'),
        # Add more types if needed (e.g., 'TF' for True/False)
    ]
    question_type = models.CharField(max_length=2, choices=QUESTION_TYPES, default='MC')

    def __str__(self):
        return self.description

    def image_url(self):
        if self.image:
            return self.image.url
        return None

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)  # mark the correct answer

    def __str__(self):
        return f"{self.text} (Question: {self.question.id})"

class Test(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    questions = models.ManyToManyField(Question, related_name='tests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    time_limit = models.IntegerField(null=True, blank=True, help_text="Time limit in minutes (optional)")

    def __str__(self):
        return self.title

    def get_total_questions(self):
        return self.questions.count()

class TestResult(models.Model):
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('TIMED_OUT', 'Timed Out'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_results')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='results')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    current_question_index = models.IntegerField(default=0)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.student.username} - {self.test.title}"

    def get_progress(self):
        total_questions = self.test.get_total_questions()
        return {
            'current': self.current_question_index + 1,
            'total': total_questions,
            'percentage': round((self.current_question_index + 1) / total_questions * 100, 1)
        }

class QuestionResponse(models.Model):
    test_result = models.ForeignKey(TestResult, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(null=True)

    def __str__(self):
        return f"{self.test_result.student.username} - {self.question.id}"

    class Meta:
        unique_together = ['test_result', 'question']

# Quest Sequence System Models
class QuestSequence(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_first_quest(self):
        return self.quests.filter(order=0).first()

class Quest(models.Model):
    sequence = models.ForeignKey(QuestSequence, on_delete=models.CASCADE, related_name='quests')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='quest')
    code = models.CharField(max_length=50, help_text="The code/password students must reveal or guess")
    order = models.IntegerField(help_text="Order within the sequence (0-based)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        unique_together = ['sequence', 'order']

    def __str__(self):
        return f"{self.sequence.title} - {self.title}"

    def get_next_quest(self):
        return Quest.objects.filter(
            sequence=self.sequence,
            order=self.order + 1
        ).first()

class QuestProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quest_progress')
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name='progress')
    revealed_letters = models.JSONField(default=list, help_text="List of revealed letter positions")
    is_completed = models.BooleanField(default=False)
    code_guessed = models.BooleanField(default=False)
    correct_answers = models.IntegerField(default=0)
    total_answers = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'quest']

    def __str__(self):
        return f"{self.student.username} - {self.quest.title}"

    def get_revealed_code(self):
        """Return the code with unrevealed letters as underscores"""
        code = self.quest.code.upper()
        revealed = ['_'] * len(code)
        
        for pos in self.revealed_letters:
            if 0 <= pos < len(code):
                revealed[pos] = code[pos]
        
        return ' '.join(revealed)

    def reveal_next_letter(self):
        """Reveal the next letter in sequence"""
        code_length = len(self.quest.code)
        for i in range(code_length):
            if i not in self.revealed_letters:
                self.revealed_letters.append(i)
                break
        self.save()

    def hide_last_letter(self):
        """Hide the last revealed letter"""
        if self.revealed_letters:
            self.revealed_letters.pop()
            self.save()

    def is_code_fully_revealed(self):
        """Check if all letters are revealed"""
        return len(self.revealed_letters) >= len(self.quest.code)

    def can_unlock_next_quest(self):
        """Check if student can unlock the next quest"""
        return self.is_completed or self.code_guessed or self.is_code_fully_revealed()

class SequenceProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sequence_progress')
    sequence = models.ForeignKey(QuestSequence, on_delete=models.CASCADE, related_name='student_progress')
    current_quest = models.ForeignKey(Quest, on_delete=models.CASCADE, null=True, blank=True)
    completed_quests = models.JSONField(default=list, help_text="List of completed quest IDs")
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'sequence']

    def __str__(self):
        return f"{self.student.username} - {self.sequence.title}"

    def get_unlocked_quests(self):
        """Get all quests that should be unlocked for this student"""
        unlocked = []
        for quest in self.sequence.quests.all():
            if quest.order == 0:  # First quest is always unlocked
                unlocked.append(quest)
            elif quest.id in self.completed_quests:
                unlocked.append(quest)
            else:
                # Check if previous quest allows unlocking
                prev_quest = Quest.objects.filter(
                    sequence=self.sequence,
                    order=quest.order - 1
                ).first()
                if prev_quest:
                    progress = QuestProgress.objects.filter(
                        student=self.student,
                        quest=prev_quest
                    ).first()
                    if progress and progress.can_unlock_next_quest():
                        unlocked.append(quest)
                        break  # Only unlock the next quest in sequence
                break
        return unlocked

    def unlock_next_quest(self, completed_quest):
        """Mark a quest as completed and unlock the next one"""
        if completed_quest.id not in self.completed_quests:
            self.completed_quests.append(completed_quest.id)
        
        next_quest = completed_quest.get_next_quest()
        if next_quest:
            self.current_quest = next_quest
        else:
            self.is_completed = True
        
        self.save()