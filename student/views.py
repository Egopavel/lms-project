from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Avg
from courses.models import Course, Lecture
from tests.models import Test, TestResult
from django.contrib import messages

@login_required
def dashboard(request):
    courses = Course.objects.filter(status='published')
    
    all_results = TestResult.objects.filter(student=request.user).order_by('-completed_at')
    results = all_results[:5]
    
    completed_count = all_results.filter(passed=True).count()
    
    context = {
        'courses': courses,
        'results': results,
        'completed_count': completed_count
    }
    return render(request, 'student/dashboard.html', context)

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id, status='published')
    
    tests = course.tests.all().prefetch_related('questions')
    lectures = course.lectures.all().order_by('order')
    
    for test in tests:
        test.attempts_count = TestResult.objects.filter(student=request.user, test=test).count()

    return render(request, 'student/course_detail.html', {
        'course': course,
        'tests': tests,
        'lectures': lectures,
    })

@login_required
def lecture_detail(request, lecture_id):
    """Просмотр лекции"""
    lecture = get_object_or_404(Lecture, id=lecture_id)
    
    if lecture.course.status != 'published':
        return redirect('student:dashboard')
    
    all_lectures = lecture.course.lectures.all().order_by('order')
    
    context = {
        'lecture': lecture,
        'all_lectures': all_lectures,
        'current_lecture': lecture,
    }
    return render(request, 'student/lecture_detail.html', context)

@login_required
def take_test(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    attempts = TestResult.objects.filter(student=request.user, test=test).count()
    
    if attempts >= test.max_attempts:
        messages.error(request, 'Вы исчерпали все попытки прохождения этого теста.')
        return redirect('student:course_detail', course_id=test.course.id)

    questions = test.questions.all().prefetch_related('answers')

    if request.method == 'POST':
        score = 0
        max_score = 0
        answers_data = {}

        for q in questions:
            max_score += q.points
            if q.question_type == 'single':
                selected = request.POST.get(f'q_{q.id}')
                if selected:
                    answers_data[str(q.id)] = selected
                    if q.answers.filter(id=selected, is_correct=True).exists():
                        score += q.points
            elif q.question_type == 'multiple':
                selected = request.POST.getlist(f'q_{q.id}')
                answers_data[str(q.id)] = selected
                
                # Получаем все правильные ответы
                correct_answers = q.answers.filter(is_correct=True)
                correct_ids = set(str(a.id) for a in correct_answers)
                selected_ids = set(selected)
                
                # Находим пересечение: то, что студент выбрал ПРАВИЛЬНО
                correct_selections = selected_ids.intersection(correct_ids)
                
                # Считаем баллы пропорционально количеству правильных выборов
                num_correct_options = len(correct_ids)
                if num_correct_options > 0:
                    points_per_option = q.points / num_correct_options
                    score += len(correct_selections) * points_per_option

        score = round(score, 2)
        passed = (score / max_score * 100) >= test.passing_score if max_score > 0 else False

        TestResult.objects.create(
            test=test,
            student=request.user,
            score=score,
            max_score=max_score,
            passed=passed,
            attempt_number=attempts + 1,
            answers_data=answers_data
        )
        messages.success(request, f'Тест завершён! Результат: {score}/{max_score}')
        return redirect('student:test_result', test_id=test.id)

    return render(request, 'student/take_test.html', {'test': test, 'questions': questions, 'attempts': attempts})

@login_required
def test_result(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    result = TestResult.objects.filter(student=request.user, test=test).order_by('-completed_at').first()
    if not result:
        return redirect('student:dashboard')
    return render(request, 'student/test_result.html', {'test': test, 'result': result})