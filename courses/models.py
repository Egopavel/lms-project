import os
from django.db import models
from django.conf import settings

def lecture_file_path(instance, filename):
    """Путь для загрузки файлов лекций"""
    ext = os.path.splitext(filename)[1]
    # Безопасный путь: используем ID курса и имя файла (без ID лекции, т.к. он ещё None при загрузке)
    return f'lectures/course_{instance.course.id}/{filename}'

class Course(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Черновик'),
        ('published', 'Опубликован'),
        ('archived', 'В архиве'),
    )
    
    title = models.CharField('Название', max_length=255)
    description = models.TextField('Описание', blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='Автор')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Lecture(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='lectures', verbose_name='Курс')
    title = models.CharField('Название лекции', max_length=255)
    content = models.TextField('Содержание', help_text='Текст лекции (можно использовать HTML)', blank=True)
    video_url = models.URLField('Ссылка на видео', blank=True, help_text='YouTube, Vimeo или другая платформа')
    
    file = models.FileField(
        'Файл лекции',
        upload_to=lecture_file_path,
        blank=True,
        null=True,
        help_text='PDF, DOC, PPT и другие форматы'
    )
    
    order = models.PositiveIntegerField('Порядковый номер', default=0, help_text='Для сортировки лекций')
    duration = models.PositiveIntegerField('Длительность (мин)', default=0, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Лекция'
        verbose_name_plural = 'Лекции'
        ordering = ['course', 'order']

    def __str__(self):
        return f"{self.course.title} — {self.title}"
    
    def file_name(self):
        """Возвращает имя файла"""
        if self.file:
            return os.path.basename(self.file.name)
        return 'Нет файла'
    file_name.short_description = 'Файл'