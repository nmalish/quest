from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import (
    Test, TestResult, QuestionResponse, Question, Answer,
    QuestSequence, Quest, QuestProgress, SequenceProgress
)
from django.db.models import Count
from django.contrib import messages

@login_required
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

@login_required
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

# Quest Sequence Views
@login_required
def quest_sequence_list(request):
    """Display list of available quest sequences"""
    sequences = QuestSequence.objects.filter(is_active=True)
    user_progress = {}
    
    for sequence in sequences:
        progress, created = SequenceProgress.objects.get_or_create(
            student=request.user,
            sequence=sequence,
            defaults={'current_quest': sequence.get_first_quest()}
        )
        user_progress[sequence.id] = progress
    
    context = {
        'sequences': sequences,
        'user_progress': user_progress
    }
    
    return render(request, 'quest/quest_sequence_list.html', context)

@login_required
def quest_sequence_detail(request, sequence_id):
    """Display a quest sequence with available quests"""
    sequence = get_object_or_404(QuestSequence, id=sequence_id, is_active=True)
    
    # Get or create sequence progress
    sequence_progress, created = SequenceProgress.objects.get_or_create(
        student=request.user,
        sequence=sequence,
        defaults={'current_quest': sequence.get_first_quest()}
    )
    
    # Get unlocked quests
    unlocked_quests = sequence_progress.get_unlocked_quests()
    
    # Get quest progress for each quest
    quest_progress = {}
    for quest in sequence.quests.all():
        progress, created = QuestProgress.objects.get_or_create(
            student=request.user,
            quest=quest
        )
        quest_progress[quest.id] = progress
    
    context = {
        'sequence': sequence,
        'sequence_progress': sequence_progress,
        'unlocked_quests': unlocked_quests,
        'quest_progress': quest_progress,
        'all_quests': sequence.quests.all()
    }
    
    return render(request, 'quest/quest_sequence_detail.html', context)

@login_required
def quest_detail(request, quest_id):
    """Display a quest with its test and code revelation"""
    quest = get_object_or_404(Quest, id=quest_id)
    
    # Check if quest is unlocked
    sequence_progress = get_object_or_404(
        SequenceProgress,
        student=request.user,
        sequence=quest.sequence
    )
    
    unlocked_quests = sequence_progress.get_unlocked_quests()
    if quest not in unlocked_quests:
        messages.error(request, "This quest is not yet unlocked.")
        return redirect('quest_sequence_detail', sequence_id=quest.sequence.id)
    
    # Get or create quest progress
    quest_progress, created = QuestProgress.objects.get_or_create(
        student=request.user,
        quest=quest
    )
    
    # Check if there's already a test in progress
    existing_result = TestResult.objects.filter(
        student=request.user,
        test=quest.test,
        status='IN_PROGRESS'
    ).first()
    
    if existing_result:
        return redirect('take_quest_test', result_id=existing_result.id)
    
    context = {
        'quest': quest,
        'quest_progress': quest_progress,
        'revealed_code': quest_progress.get_revealed_code(),
        'can_guess': True
    }
    
    return render(request, 'quest/quest_detail.html', context)

@login_required
def start_quest_test(request, quest_id):
    """Start a quest test session"""
    quest = get_object_or_404(Quest, id=quest_id)
    
    # Check if quest is unlocked
    sequence_progress = get_object_or_404(
        SequenceProgress,
        student=request.user,
        sequence=quest.sequence
    )
    
    unlocked_quests = sequence_progress.get_unlocked_quests()
    if quest not in unlocked_quests:
        messages.error(request, "This quest is not yet unlocked.")
        return redirect('quest_sequence_detail', sequence_id=quest.sequence.id)
    
    # Check if there's already an in-progress test
    existing_result = TestResult.objects.filter(
        student=request.user,
        test=quest.test,
        status='IN_PROGRESS'
    ).first()
    
    if existing_result:
        return redirect('take_quest_test', result_id=existing_result.id)
    
    # Create new test result
    test_result = TestResult.objects.create(
        student=request.user,
        test=quest.test,
        status='IN_PROGRESS'
    )
    
    return redirect('take_quest_test', result_id=test_result.id)

@login_required
def take_quest_test(request, result_id):
    """Handle quest test taking with code revelation"""
    test_result = get_object_or_404(TestResult, id=result_id, student=request.user)
    
    # Get the quest associated with this test
    quest = get_object_or_404(Quest, test=test_result.test)
    
    # Get quest progress
    quest_progress = get_object_or_404(
        QuestProgress,
        student=request.user,
        quest=quest
    )
    
    if test_result.status != 'IN_PROGRESS':
        return redirect('quest_test_result', result_id=result_id)
    
    # Get current question
    questions = list(test_result.test.questions.all())
    if not questions:
        messages.error(request, "No questions found in this test.")
        return redirect('quest_detail', quest_id=quest.id)
    
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
            
            # Update quest progress based on answer
            quest_progress.total_answers += 1
            if answer.is_correct:
                quest_progress.correct_answers += 1
                quest_progress.reveal_next_letter()
            else:
                quest_progress.hide_last_letter()
            quest_progress.save()
            
            # Move to next question or complete test
            if test_result.current_question_index < len(questions) - 1:
                test_result.current_question_index += 1
                test_result.save()
                return redirect('take_quest_test', result_id=result_id)
            else:
                test_result.status = 'COMPLETED'
                test_result.completed_at = timezone.now()
                test_result.save()
                return redirect('quest_test_result', result_id=result_id)
    
    # Calculate progress
    progress = test_result.get_progress()
    
    context = {
        'test_result': test_result,
        'quest': quest,
        'quest_progress': quest_progress,
        'current_question': current_question,
        'progress': progress,
        'total_questions': len(questions),
        'revealed_code': quest_progress.get_revealed_code()
    }
    
    return render(request, 'quest/take_quest_test.html', context)

@login_required
def quest_test_result(request, result_id):
    """Display quest test results with code revelation"""
    test_result = get_object_or_404(TestResult, id=result_id, student=request.user)
    
    # Get the quest associated with this test
    quest = get_object_or_404(Quest, test=test_result.test)
    
    # Get quest progress
    quest_progress = get_object_or_404(
        QuestProgress,
        student=request.user,
        quest=quest
    )
    
    # Calculate score if not already set
    if test_result.score is None:
        correct_responses = test_result.responses.filter(is_correct=True).count()
        total_questions = test_result.test.get_total_questions()
        if total_questions > 0:
            test_result.score = (correct_responses / total_questions) * 100
            test_result.save()
    
    context = {
        'test_result': test_result,
        'quest': quest,
        'quest_progress': quest_progress,
        'revealed_code': quest_progress.get_revealed_code(),
        'responses': test_result.responses.all().select_related('question', 'selected_answer'),
        'can_guess_code': not quest_progress.is_completed and not quest_progress.code_guessed
    }
    
    return render(request, 'quest/quest_test_result.html', context)

@login_required
@require_POST
def guess_code(request, quest_id):
    """Handle code guessing for a quest"""
    quest = get_object_or_404(Quest, id=quest_id)
    
    # Get quest progress
    quest_progress = get_object_or_404(
        QuestProgress,
        student=request.user,
        quest=quest
    )
    
    guessed_code = request.POST.get('guessed_code', '').strip().upper()
    
    if guessed_code == quest.code.upper():
        # Correct guess
        quest_progress.code_guessed = True
        quest_progress.is_completed = True
        quest_progress.save()
        
        # Update sequence progress
        sequence_progress = get_object_or_404(
            SequenceProgress,
            student=request.user,
            sequence=quest.sequence
        )
        sequence_progress.unlock_next_quest(quest)
        
        messages.success(request, f"Congratulations! You've cracked the code: {quest.code}")
        return JsonResponse({'success': True, 'message': 'Code cracked successfully!'})
    else:
        # Incorrect guess
        messages.error(request, "Incorrect code. Keep trying!")
        return JsonResponse({'success': False, 'message': 'Incorrect code. Keep trying!'})

@login_required
def quest_home(request):
    """Main quest home page - redirect to sequence list"""
    return redirect('quest_sequence_list')