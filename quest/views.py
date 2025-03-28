from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Test, TestResult, QuestionResponse, Question, Answer
from django.db.models import Count
from django.contrib import messages

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

@login_required
def test_list(request):
    """Display list of available tests"""
    tests = Test.objects.all()
    return render(request, 'quest/test_list.html', {'tests': tests})

@login_required
def start_test(request, test_id):
    """Start a new test session"""
    test = get_object_or_404(Test, id=test_id)
    
    # Check if there's already an in-progress test
    existing_result = TestResult.objects.filter(
        student=request.user,
        test=test,
        status='IN_PROGRESS'
    ).first()
    
    if existing_result:
        return redirect('take_test', result_id=existing_result.id)
    
    # Create new test result
    test_result = TestResult.objects.create(
        student=request.user,
        test=test,
        status='IN_PROGRESS'
    )
    
    return redirect('take_test', result_id=test_result.id)

@login_required
def take_test(request, result_id):
    """Display and handle the test-taking process"""
    test_result = get_object_or_404(TestResult, id=result_id, student=request.user)
    
    if test_result.status != 'IN_PROGRESS':
        return redirect('test_result', result_id=result_id)
    
    # Get current question
    questions = list(test_result.test.questions.all())
    if not questions:
        messages.error(request, "No questions found in this test.")
        return redirect('test_list')
    
    current_question = questions[test_result.current_question_index]
    
    # Handle answer submission
    if request.method == 'POST':
        answer_id = request.POST.get('answer')
        if answer_id:
            answer = get_object_or_404(Answer, id=answer_id, question=current_question)
            
            # Create or update question response
            QuestionResponse.objects.update_or_create(
                test_result=test_result,
                question=current_question,
                defaults={
                    'selected_answer': answer,
                    'is_correct': answer.is_correct
                }
            )
            
            # Move to next question or complete test
            if test_result.current_question_index < len(questions) - 1:
                test_result.current_question_index += 1
                test_result.save()
                return redirect('take_test', result_id=result_id)
            else:
                test_result.status = 'COMPLETED'
                test_result.completed_at = timezone.now()
                test_result.save()
                return redirect('test_result', result_id=result_id)
    
    # Calculate progress
    progress = test_result.get_progress()
    
    context = {
        'test_result': test_result,
        'current_question': current_question,
        'progress': progress,
        'total_questions': len(questions)
    }
    
    return render(request, 'quest/take_test.html', context)

@login_required
def test_result(request, result_id):
    """Display test results"""
    test_result = get_object_or_404(TestResult, id=result_id, student=request.user)
    
    # Calculate score if not already set
    if test_result.score is None:
        correct_responses = test_result.responses.filter(is_correct=True).count()
        total_questions = test_result.test.get_total_questions()
        if total_questions > 0:
            test_result.score = (correct_responses / total_questions) * 100
            test_result.save()
    
    context = {
        'test_result': test_result,
        'responses': test_result.responses.all().select_related('question', 'selected_answer')
    }
    
    return render(request, 'quest/test_result.html', context)