from django.contrib import admin
from .models import Test, Question, Answer, TestResult, StudentProfile, TeacherProfile
from accounts.models import CustomUser # Импорт нужен, но регистрировать здесь НЕ надо

# ===== Профили =====
class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name = 'Профиль студента'
    verbose_name_plural = 'Профиль студента'

class TeacherProfileInline(admin.StackedInline):
    model = TeacherProfile
    can_delete = False
    verbose_name = 'Профиль преподавателя'
    verbose_name_plural = 'Профиль преподавателя'

# ===== Ответы (варианты) =====
class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 3
    fields = ('text', 'is_correct', 'order')
    ordering = ('order',)

# ===== Вопросы =====
class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    fields = ('text', 'question_type', 'points', 'order')
    ordering = ('order',)
    show_change_link = True

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'test', 'question_type', 'points', 'order')
    list_filter = ('question_type', 'test')
    search_fields = ('text',)
    ordering = ('test', 'order')
    inlines = [AnswerInline]

# ===== Тесты =====
@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'time_limit', 'passing_score', 'max_attempts', 'created_at')
    list_filter = ('course', 'created_at')
    search_fields = ('title',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    inlines = [QuestionInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'course')
        }),
        ('Настройки', {
            'fields': ('time_limit', 'passing_score', 'max_attempts')
        }),
        ('Даты', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at',)

# ===== Результаты тестов =====
@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('test', 'student', 'score', 'max_score', 'passed', 'attempt_number', 'completed_at')
    list_filter = ('passed', 'completed_at', 'test')
    search_fields = ('student__username', 'student__email', 'test__title')
    ordering = ('-completed_at',)
    date_hierarchy = 'completed_at'
    readonly_fields = ('test', 'student', 'score', 'max_score', 'passed', 
                       'attempt_number', 'completed_at', 'answers_data')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

