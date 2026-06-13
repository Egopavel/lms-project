from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from courses.models import Course
from tests.models import Test, TestResult, Question
from accounts.models import CustomUser

@login_required
def dashboard(request):
    """Панель преподавателя - только свои курсы и студенты"""
    if request.user.role not in ['teacher', 'admin']:
        return redirect('student:dashboard')
    
    # Фильтруем курсы
    if request.user.is_superuser or request.user.role == 'admin':
        courses = Course.objects.all()
    else:
        courses = Course.objects.filter(author=request.user)
    
    # 🔥 ИСПРАВЛЕНО: Получаем студентов через ManyToMany (related_name='teachers')
    if request.user.is_superuser or request.user.role == 'admin':
        my_students = CustomUser.objects.filter(role='student')
    else:
        my_students = CustomUser.objects.filter(teachers=request.user, role='student')
    
    total_students = my_students.count()
    total_tests = Test.objects.filter(course__in=courses).count()
    total_results = TestResult.objects.filter(test__course__in=courses, student__in=my_students).count()
    avg_score = TestResult.objects.filter(test__course__in=courses, student__in=my_students).aggregate(
        avg=Avg('score')
    )['avg'] or 0
    
    recent_results = TestResult.objects.filter(
        test__course__in=courses,
        student__in=my_students
    ).select_related('student', 'test').order_by('-completed_at')[:10]
    
    context = {
        'courses': courses,
        'total_students': total_students,
        'total_tests': total_tests,
        'total_results': total_results,
        'avg_score': round(avg_score, 2),
        'recent_results': recent_results,
    }
    return render(request, 'teacher/dashboard.html', context)

@login_required
def my_students(request):
    """Список студентов преподавателя"""
    if request.user.role not in ['teacher', 'admin']:
        return redirect('student:dashboard')
    
    # 🔥 ИСПРАВЛЕНО: Фильтр через teachers (ManyToMany)
    if request.user.is_superuser or request.user.role == 'admin':
        students = CustomUser.objects.filter(role='student')
    else:
        students = CustomUser.objects.filter(teachers=request.user, role='student')
    
    students = students.annotate(
        tests_passed=Count('test_results', filter=Q(test_results__passed=True)),
        tests_total=Count('test_results'),
        avg_score=Avg('test_results__score')
    )
    
    return render(request, 'teacher/my_students.html', {'students': students})

@login_required
def course_list(request):
    """Список всех курсов"""
    if request.user.is_superuser or request.user.role == 'admin':
        courses = Course.objects.all().annotate(
            tests_count=Count('tests'),
            students_count=Count('tests__results', distinct=True)
        )
    else:
        courses = Course.objects.filter(author=request.user).annotate(
            tests_count=Count('tests'),
            students_count=Count('tests__results', distinct=True)
        )
    
    return render(request, 'teacher/course_list.html', {'courses': courses})

@login_required
def course_detail(request, course_id):
    """Детальная информация о курсе"""
    course = get_object_or_404(Course, id=course_id)
    
    if request.user.role not in ['teacher', 'admin'] and course.author != request.user:
        return redirect('teacher:dashboard')
    
    tests = course.tests.all().prefetch_related('questions')
    
    for test in tests:
        test.results_count = TestResult.objects.filter(test=test).count()
        test.avg_score = TestResult.objects.filter(test=test).aggregate(
            avg=Avg('score')
        )['avg'] or 0
        test.pass_rate = TestResult.objects.filter(test=test, passed=True).count()
    
    return render(request, 'teacher/course_detail.html', {
        'course': course,
        'tests': tests,
    })

@login_required
def student_progress(request, student_id):
    """Прогресс конкретного студента"""
    student = get_object_or_404(CustomUser, id=student_id, role='student')
    
    # 🔥 ИСПРАВЛЕНО: Проверка доступа через teachers
    if request.user.role not in ['teacher', 'admin']:
        if not student.teachers.filter(id=request.user.id).exists():
            return redirect('teacher:my_students')
    
    results = TestResult.objects.filter(
        student=student
    ).select_related('test__course').order_by('-completed_at')
    
    total_tests = results.count()
    passed_tests = results.filter(passed=True).count()
    avg_score = results.aggregate(avg=Avg('score'))['avg'] or 0
    
    context = {
        'student': student,
        'results': results,
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'avg_score': round(avg_score, 2),
    }
    return render(request, 'teacher/student_progress.html', context)

@login_required
def test_results(request, test_id):
    """Результаты конкретного теста"""
    test = get_object_or_404(Test, id=test_id)
    
    if request.user.role not in ['teacher', 'admin'] and test.course.author != request.user:
        return redirect('teacher:dashboard')
    
    results = TestResult.objects.filter(
        test=test
    ).select_related('student').order_by('-score', '-completed_at')
    
    total_attempts = results.count()
    passed_count = results.filter(passed=True).count()
    avg_score = results.aggregate(avg=Avg('score'))['avg'] or 0
    
    context = {
        'test': test,
        'results': results,
        'total_attempts': total_attempts,
        'passed_count': passed_count,
        'avg_score': round(avg_score, 2),
        'pass_rate': round(passed_count / total_attempts * 100, 1) if total_attempts > 0 else 0,
    }
    return render(request, 'teacher/test_results.html', context)