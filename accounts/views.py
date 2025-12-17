from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout



# PATIENT SIGNUP
def patient_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('patient_signup')

        user = User.objects.create_user(username=username, password=password)

        user.profile.role = 'patient'
        user.profile.save()

        login(request, user)
        return redirect('patient_dashboard')

    return render(request, 'accounts/patient_signup.html')


# DOCTOR SIGNUP
def doctor_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('doctor_signup')

        user = User.objects.create_user(username=username, password=password)

        user.profile.role = 'doctor'
        user.profile.save()   # FIXED

        login(request, user)
        return redirect('doctor_dashboard')

    return render(request, 'accounts/doctor_signup.html')


# LOGIN
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.profile.role == 'doctor':
                return redirect('doctor_dashboard')
            else:
                return redirect('patient_dashboard')
        else:
            messages.error(request, 'Invalid credentials')

    return render(request, 'accounts/login.html')



# DASHBOARDS
@login_required
def patient_dashboard(request):
    return render(request, 'accounts/patient_dashboard.html')


@login_required
def doctor_dashboard(request):
    return render(request, 'accounts/doctor_dashboard.html')

def user_logout(request):
    logout(request)
    return redirect('login')
