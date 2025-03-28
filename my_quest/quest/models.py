from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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