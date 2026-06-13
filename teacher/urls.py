from django.urls import path
from . import views

app_name = 'teacher'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('students/', views.my_students, name='my_students'),  # Новый маршрут
    path('courses/', views.course_list, name='course_list'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('student/<int:student_id>/', views.student_progress, name='student_progress'),
    path('test/<int:test_id>/results/', views.test_results, name='test_results'),
]