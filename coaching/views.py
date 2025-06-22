from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .models import Course, Student, StudyMaterial, Assignment, Message, Result, Announcement, Attendance
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.models import User, Group
import os
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone

# Global flag for admin approval (in production, use a model or setting)
ALLOW_TEACHER_REGISTRATION = True

def home(request):
    return render(request, 'coaching/home.html')

def course_list(request):
    courses = Course.objects.all()
    enrolled = []
    if request.user.is_authenticated:
        try:
            student = Student.objects.get(email=request.user.email)
            enrolled = student.enrolled_courses.values_list('id', flat=True)
            if request.method == 'POST':
                course_id = request.POST.get('course_id')
                if course_id:
                    course = Course.objects.get(id=course_id)
                    student.enrolled_courses.add(course)
                    enrolled = student.enrolled_courses.values_list('id', flat=True)
        except Student.DoesNotExist:
            pass
    return render(request, 'coaching/course_list.html', {'courses': courses, 'enrolled': enrolled})

def student_list(request):
    students = Student.objects.all()
    return render(request, 'coaching/student_list.html', {'students': students})

def teacher_list(request):
    students = Student.objects.all()
    return render(request, 'coaching/teacher_list.html', {'students': students})

def contact(request):
    return render(request, 'coaching/contact.html')

def teacher_login(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('teacher_dashboard')
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.groups.filter(name='Teachers').exists():
            login(request, user)
            return redirect('teacher_dashboard')
        else:
            error = 'Invalid credentials or not a teacher account.'
    return render(request, 'coaching/teacher_login.html', {'error': error})

def teacher_dashboard(request):
    students_count = Student.objects.count()
    courses_count = Course.objects.count()
    context = {
        'students_count': students_count,
        'courses_count': courses_count,
    }
    return render(request, 'coaching/teacher_dashboard.html', context)


def add_course(request):
    error = None
    success = None
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        image = request.FILES.get('image')
        if not name:
            error = 'Course name is required.'
        elif not start_date or not end_date:
            error = 'Start date and end date are required.'
        else:
            Course.objects.create(name=name, description=description, start_date=start_date, end_date=end_date, image=image)
            success = 'Course added successfully!'
    return render(request, 'coaching/add_course.html', {'error': error, 'success': success})

def student_dashboard(request):
    enrolled_courses = []
    available_courses = []
    if request.user.is_authenticated:
        try:
            student = Student.objects.get(email=request.user.email)
            enrolled_courses = student.enrolled_courses.all()
            enrolled_ids = enrolled_courses.values_list('id', flat=True)
            available_courses = Course.objects.exclude(id__in=enrolled_ids)
        except Student.DoesNotExist:
            available_courses = Course.objects.all()
    context = {
        'enrolled_courses': enrolled_courses,
        'available_courses': available_courses,
    }
    return render(request, 'coaching/student_dashboard.html', context)

@user_passes_test(lambda u: u.is_superuser)
def admin_manage_teachers(request):
    teachers = User.objects.filter(groups__name='Teachers')
    return render(request, 'coaching/admin_manage_teachers.html', {'teachers': teachers})

def teacher_register(request):
    error = None
    success = None
    if request.method == 'POST':
        if not ALLOW_TEACHER_REGISTRATION:
            error = 'Teacher registration is currently disabled by admin.'
        else:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            if User.objects.filter(username=username).exists():
                error = 'Username already exists.'
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                # Add to Teachers group if exists
                group, _ = Group.objects.get_or_create(name='Teachers')
                user.groups.add(group)
                user.save()
                success = 'Account created successfully! You can now log in.'
    return render(request, 'coaching/teacher_register.html', {'error': error, 'success': success})

def student_register(request):
    from .models import Course
    error = None
    success = None
    courses = Course.objects.all()
    if request.method == 'POST':
        name = request.POST.get('first_name', '') + ' ' + request.POST.get('last_name', '')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        password = request.POST.get('password')
        selected_courses = request.POST.getlist('courses')
        if Student.objects.filter(email=email).exists():
            error = 'Email already exists.'
        else:
            student = Student.objects.create(
                name=name.strip(),
                email=email,
                phone=phone,
                address=address,
                dob=dob if dob else None,
                gender=gender
            )
            if selected_courses:
                student.enrolled_courses.set(selected_courses)
            student.save()
            success = 'Account created successfully! You can now log in.'
    return render(request, 'coaching/student_register.html', {'error': error, 'success': success, 'courses': courses})

def student_login(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('student_dashboard')
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        # You can add a group check for students if you use groups
        if user is not None:
            login(request, user)
            return redirect('student_dashboard')
        else:
            error = 'Invalid credentials or not a student account.'
    return render(request, 'coaching/student_login.html', {'error': error})

def admin_login(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('admin_dashboard')
    from django.contrib.auth import authenticate, login
    from django.shortcuts import render, redirect
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            error = 'Invalid credentials or not an admin account.'
    return render(request, 'coaching/admin_login.html', {'error': error})

def about(request):
    return render(request, 'coaching/about.html')

def admin_dashboard(request):
    # You can add more admin-specific context here if needed
    return render(request, 'coaching/admin_dashboard.html')

def mark_attendance(request):
    students = Student.objects.all()
    courses = Course.objects.all()
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        date = request.POST.get('date')
        present_ids = request.POST.getlist('present')
        course = Course.objects.get(id=course_id) if course_id else None
        for student in students:
            if str(student.id) in present_ids:
                Attendance.objects.create(student=student, date=date, status=True)
            else:
                Attendance.objects.create(student=student, date=date, status=False)
        messages.success(request, 'Attendance marked successfully!')
        return redirect('mark_attendance')
    return render(request, 'coaching/mark_attendance.html', {'students': students, 'courses': courses})

def view_analytics(request):
    return render(request, 'coaching/view_analytics.html')

def upload_study_material(request):
    return render(request, 'coaching/upload_study_material.html')

def study_materials(request):
    materials = StudyMaterial.objects.all()
    if request.method == 'POST' and request.FILES.get('file'):
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        course_id = request.POST.get('course')
        file = request.FILES['file']
        course = Course.objects.get(id=course_id)
        StudyMaterial.objects.create(title=title, description=description, file=file, uploaded_by=request.user, course=course)
        return HttpResponseRedirect(reverse('study_materials'))
    return render(request, 'coaching/study_materials.html', {'materials': materials})

def assignments(request):
    from django.core.files.storage import FileSystemStorage
    assignments_dir = os.path.join('coaching', 'static', 'assignments')
    os.makedirs(assignments_dir, exist_ok=True)
    success = None
    error = None
    # Handle delete
    if request.method == 'POST' and request.GET.get('delete'):
        file_to_delete = request.GET['delete']
        file_path = os.path.join(assignments_dir, file_to_delete)
        if os.path.exists(file_path):
            os.remove(file_path)
            success = f"Assignment '{file_to_delete}' deleted successfully!"
        else:
            error = 'File not found.'
    # Handle upload
    elif request.method == 'POST' and request.FILES.get('assignment_file'):
        uploaded_file = request.FILES['assignment_file']
        fs = FileSystemStorage(location=assignments_dir)
        filename = fs.save(uploaded_file.name, uploaded_file)
        success = f"Assignment '{uploaded_file.name}' uploaded successfully!"
    elif request.method == 'POST':
        error = 'Please select a file to upload.'
    # List assignments
    try:
        assignments = [f for f in os.listdir(assignments_dir) if not f.startswith('.')]
    except Exception:
        assignments = []
    return render(request, 'coaching/assignments.html', {'success': success, 'error': error, 'assignments': assignments})

def assignments_list(request):
    assignments = Assignment.objects.all()
    return render(request, 'coaching/assignments_list.html', {'assignments': assignments})

def upload_assignment(request):
    if request.method == 'POST' and request.FILES.get('file'):
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        course_id = request.POST.get('course')
        due_date = request.POST.get('due_date')
        file = request.FILES['file']
        course = Course.objects.get(id=course_id)
        Assignment.objects.create(title=title, description=description, file=file, course=course, assigned_by=request.user, due_date=due_date)
        return HttpResponseRedirect(reverse('assignments_list'))
    courses = Course.objects.all()
    return render(request, 'coaching/upload_assignment.html', {'courses': courses})

def messages_view(request):
    messages_qs = Message.objects.filter(receiver=request.user) | Message.objects.filter(sender=request.user)
    messages_qs = messages_qs.order_by('-sent_at')
    if request.method == 'POST':
        content = request.POST.get('content')
        receiver_id = request.POST.get('receiver')
        receiver = User.objects.get(id=receiver_id)
        Message.objects.create(sender=request.user, receiver=receiver, content=content)
        return HttpResponseRedirect(reverse('messages_view'))
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'coaching/messages.html', {'messages': messages_qs, 'users': users})

def results_view(request):
    if request.user.groups.filter(name='Teachers').exists():
        results = Result.objects.all()
    else:
        try:
            student = Student.objects.get(email=request.user.email)
            results = Result.objects.filter(student=student)
        except Student.DoesNotExist:
            results = Result.objects.none()
    return render(request, 'coaching/results.html', {'results': results})

def upload_result(request):
    if request.method == 'POST' and request.FILES.get('file'):
        student_id = request.POST.get('student')
        course_id = request.POST.get('course')
        marks = request.POST.get('marks')
        file = request.FILES['file']
        description = request.POST.get('description', '')
        student = Student.objects.get(id=student_id)
        course = Course.objects.get(id=course_id)
        Result.objects.create(student=student, course=course, marks=marks, file=file, description=description)
        return HttpResponseRedirect(reverse('results_view'))
    students = Student.objects.all()
    courses = Course.objects.all()
    return render(request, 'coaching/upload_result.html', {'students': students, 'courses': courses})

def announcements_view(request):
    # Only allow creation if not a student
    is_student = False
    if request.user.is_authenticated:
        for group in request.user.groups.all():
            if group.name.lower() == 'students':
                is_student = True
                break
    announcements = Announcement.objects.filter(for_all=True) | Announcement.objects.filter(for_role__in=[g.name.lower() for g in request.user.groups.all()])
    announcements = announcements.order_by('-created_at')
    if request.method == 'POST' and not is_student:
        title = request.POST.get('title')
        content = request.POST.get('content')
        file = request.FILES.get('file')
        for_all = bool(request.POST.get('for_all'))
        for_role = request.POST.get('for_role', '')
        Announcement.objects.create(title=title, content=content, file=file, created_by=request.user, for_all=for_all, for_role=for_role)
        return HttpResponseRedirect(reverse('announcements_view'))
    return render(request, 'coaching/announcements.html', {'announcements': announcements, 'is_student': is_student})

def edit_course(request, course_id):
    course = Course.objects.get(id=course_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        course.name = name
        course.description = description
        course.save()
        messages.success(request, 'Course updated successfully!')
        return redirect('course_list')
    return render(request, 'coaching/edit_course.html', {'course': course})

def delete_course(request, course_id):
    if not request.user.is_superuser:
        return redirect('course_list')
    course = Course.objects.get(id=course_id)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully!')
        return redirect('course_list')
    return redirect('course_list')

def enroll_course(request, course_id):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to enroll in a course.")
        return redirect('course_list')
    try:
        student = Student.objects.get(email=request.user.email)
        course = Course.objects.get(id=course_id)
        if course not in student.enrolled_courses.all():
            student.enrolled_courses.add(course)
            messages.success(request, f"Enrolled in {course.name} successfully!")
        else:
            messages.info(request, f"You are already enrolled in {course.name}.")
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
    except Course.DoesNotExist:
        messages.error(request, "Course not found.")
    return redirect('course_list')
