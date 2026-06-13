from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'department', 'get_students_count', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    # 🔥 ЭТА СТРОКА ВКЛЮЧАЕТ ИНТЕРФЕЙС "ДВА СПИСКА С КНОПКАМИ +" И "-"
    filter_horizontal = ('students',)

    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'department'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'department'),
        }),
    )

    # Показываем блок студентов только в карточке преподавателя
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj and obj.role == 'teacher':
            fieldsets = fieldsets + (
                ('Закреплённые студенты', {
                    'fields': ('students',),
                }),
            )
        return fieldsets

    # Вспомогательный метод для отображения количества в списке
    def get_students_count(self, obj):
        if obj.role == 'teacher':
            return obj.students.count()
        return '-'
    get_students_count.short_description = 'Студентов'

    # Массовое действие (оставляем как было)
    actions = ['assign_students_to_teacher']

    @admin.action(description='Закрепить студентов за преподавателем')
    def assign_students_to_teacher(self, request, queryset):
        students = queryset.filter(role='student')
        if students.count() == 0:
            self.message_user(request, 'Выберите хотя бы одного студента', 'warning')
            return
        
        teachers = CustomUser.objects.filter(role='teacher')
        if teachers.count() == 0:
            self.message_user(request, 'Нет доступных преподавателей', 'error')
            return
        
        teacher = teachers.first()
        teacher.students.add(*students)
        self.message_user(
            request,
            f'{students.count()} студентов закреплено за {teacher.get_full_name() or teacher.username}',
            'success'
        )