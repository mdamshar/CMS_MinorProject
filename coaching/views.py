from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .models import Course, Student
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User, Group

# Global flag for admin approval (in production, use a model or setting)
ALLOW_TEACHER_REGISTRATION = True

def home(request):
    return render(request, 'coaching/home.html')

def course_list(request):
    courses = Course.objects.all()
    return render(request, 'coaching/course_list.html', {'courses': courses})

def student_list(request):
    students = Student.objects.all()
    return render(request, 'coaching/student_list.html', {'students': students})

def teacher_list(request):
    # Placeholder for teacher list view
    return render(request, 'coaching/teacher_list.html')

def contact(request):
    return render(request, 'coaching/contact.html')

def teacher_login(request):
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
    # You can add context for the teacher dashboard here
    return render(request, 'coaching/teacher_list.html')

def student_dashboard(request):
    # You can add context for the student dashboard here
    return render(request, 'coaching/student_list.html')

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
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        selected_courses = request.POST.getlist('courses')
        if User.objects.filter(username=username).exists():
            error = 'Username already exists.'
        else:
            user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
            user.save()
            try:
                student = Student.objects.create(user=user, dob=dob, gender=gender, phone=phone, address=address)
                student.courses.set(selected_courses)
                student.save()
            except Exception:
                pass  # If no Student model or M2M, skip
            success = 'Account created successfully! You can now log in.'
    return render(request, 'coaching/student_register.html', {'error': error, 'success': success, 'courses': courses})

def student_login(request):
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
