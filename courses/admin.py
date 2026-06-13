from django.contrib import admin
from django.utils.html import format_html
from .models import Course, Lecture

class LectureInline(admin.TabularInline):
    model = Lecture
    extra = 1
    fields = ('title', 'order', 'duration', 'file')
    ordering = ('order',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'created_at', 'lectures_count')
    list_filter = ('status', 'created_at', 'author')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    inlines = [LectureInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'author', 'status')
        }),
        ('Даты', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at',)
    
    def lectures_count(self, obj):
        return obj.lectures.count()
    lectures_count.short_description = 'Лекций'

@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'duration', 'file_download_link', 'created_at')
    list_filter = ('course', 'created_at')
    search_fields = ('title', 'content')
    ordering = ('course', 'order')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('course', 'title', 'content', 'order')
        }),
        ('Мультимедиа', {
            'fields': ('video_url', 'duration', 'file')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def file_download_link(self, obj):
        if obj.file:
            return format_html(
                '<a href="{}" target="_blank" class="button">📄 Скачать</a>',
                obj.file.url
            )
        return 'Нет файла'
    file_download_link.short_description = 'Файл'