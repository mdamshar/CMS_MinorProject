from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.course_list, name='course_list'),
    path('students/', views.student_list, name='student_list'),
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('contact/', views.contact, name='contact'),
    path('teacher-login/', views.teacher_login, name='teacher_login'),
    path('student-login/', views.student_login, name='student_login'),
    path('admin/manage-teachers/', views.admin_manage_teachers, name='admin_manage_teachers'),
    path('teacher-register/', views.teacher_register, name='teacher_register'),
    path('student-register/', views.student_register, name='student_register'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
]
