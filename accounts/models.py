from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Администратор'),
        ('teacher', 'Преподаватель'),
        ('student', 'Студент'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    department = models.CharField('Подразделение', max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    
    # ManyToMany для связи преподаватель ↔ студенты
    students = models.ManyToManyField(
        'self',
        symmetrical=False,  # Важно: связь не симметричная
        limit_choices_to={'role': 'student'},  # Показываем только студентов
        blank=True,
        related_name='teachers',
        verbose_name='Закреплённые студенты'
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'