from django.db import models
from django.conf import settings
from courses.models import Course  # создадим позже

# ===== СТУДЕНТЫ (расширение пользователя) =====
class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    group = models.CharField('Группа', max_length=50, blank=True)
    enrollment_date = models.DateField('Дата зачисления', auto_now_add=True)

    class Meta:
        verbose_name = 'Профиль студента'
        verbose_name_plural = 'Профили студентов'

# ===== ПРЕПОДАВАТЕЛИ =====
class TeacherProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher_profile')
    specialization = models.CharField('Специализация', max_length=100, blank=True)
    hire_date = models.DateField('Дата найма', auto_now_add=True)

    class Meta:
        verbose_name = 'Профиль преподавателя'
        verbose_name_plural = 'Профили преподавателей'

# ===== ТЕСТЫ =====
class Test(models.Model):
    title = models.CharField('Название теста', max_length=255)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='tests', verbose_name='Курс')
    time_limit = models.PositiveIntegerField('Время (мин)', default=60)
    passing_score = models.PositiveIntegerField('Проходной балл (%)', default=70)
    max_attempts = models.PositiveIntegerField('Макс. попыток', default=3)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'

    def __str__(self):
        return self.title

# ===== ВОПРОСЫ =====
class Question(models.Model):
    QUESTION_TYPES = (
        ('single', 'Один правильный ответ'),
        ('multiple', 'Несколько правильных'),
        ('text', 'Текстовый ответ'),
    )
    
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions', verbose_name='Тест')
    text = models.TextField('Текст вопроса')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='single')
    points = models.PositiveIntegerField('Баллы', default=1)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['order']

    def __str__(self):
        return f"Вопрос {self.pk}: {self.text[:50]}..."

# ===== ОТВЕТЫ (варианты для тестовых вопросов) =====
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name='Вопрос')
    text = models.CharField('Текст ответа', max_length=500)
    is_correct = models.BooleanField('Правильный', default=False)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответов'
        ordering = ['order']

    def __str__(self):
        return self.text

# ===== РЕЗУЛЬТАТЫ ТЕСТОВ =====
class TestResult(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='results', verbose_name='Тест')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='test_results', verbose_name='Студент')
    score = models.PositiveIntegerField('Набрано баллов')
    max_score = models.PositiveIntegerField('Макс. баллов')
    passed = models.BooleanField('Сдан', default=False)
    attempt_number = models.PositiveIntegerField('Попытка', default=1)
    completed_at = models.DateTimeField(auto_now_add=True)
    answers_data = models.JSONField('Ответы студента', blank=True, default=dict)

    class Meta:
        verbose_name = 'Результат теста'
        verbose_name_plural = 'Результаты тестов'
        ordering = ['-completed_at']

    def __str__(self):
        status = "✓" if self.passed else "✗"
        return f"{status} {self.student.username} — {self.test.title} ({self.score}/{self.max_score})"