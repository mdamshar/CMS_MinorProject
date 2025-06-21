from django.contrib import admin
from .models import Course, Student, Attendance, Fee

admin.site.register(Course)
admin.site.register(Student)
admin.site.register(Attendance)
admin.site.register(Fee)
