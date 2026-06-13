from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from accounts import views as auth_views

# Функция для перенаправления
def home_redirect(request):
    return redirect('login')

urlpatterns = [
    path('', home_redirect, name='home'),  # ← ДОБАВИТЬ ЭТУ СТРОКУ
    path('admin/', admin.site.urls),
    path('login/', auth_views.custom_login, name='login'),
    path('logout/', auth_views.custom_logout, name='logout'),
    path('dashboard/', auth_views.dashboard, name='dashboard'),
    path('student/', include('student.urls', namespace='student')),
    path('teacher/', include('teacher.urls', namespace='teacher')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)