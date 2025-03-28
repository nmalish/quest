from django.db import models

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