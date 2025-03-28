from django.shortcuts import render
from django.http import JsonResponse
from .models import Question

def get_questions(request):
    questions = Question.objects.prefetch_related('answers').all()
    data = [
        {
            "id": q.id,
            "description": q.description,
            "image": q.image.url if q.image else None,
            "type": q.type,
            "answers": [
                {"id": a.id, "description": a.description, "is_correct": a.is_correct}
                for a in q.answers.all()
            ]
        }
        for q in questions
    ]
    return JsonResponse({"questions": data}, safe=False)

def questions_list(request):
    questions = Question.objects.prefetch_related('answers').all()
    return render(request, 'quest/questions_list.html', {'questions': questions})