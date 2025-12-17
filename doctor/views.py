from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import DoctorAvailability, Booking
from .forms import AvailabilityForm
from .google_calendar import get_google_auth_url, exchange_code_for_tokens


@login_required
def dashboard(request):
    user = request.user
    if getattr(user, 'role', None) != 'doctor':
        messages.error(request, 'Only doctors can access the doctor dashboard.')
        return redirect('dashboard')

    availabilities = DoctorAvailability.objects.filter(doctor=user).order_by('date', 'start_time')
    bookings = Booking.objects.filter(doctor=user).order_by('-created_at')

    context = {
        'availabilities': availabilities,
        'bookings': bookings,
    }
    return render(request, 'doctor_assistant/dashboard.html', context)


@login_required
def add_availability(request):
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied.')
        return redirect('home')

    if request.method == 'POST':
        form = AvailabilityForm(request.POST, doctor=request.user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Availability slot added successfully!')
                return redirect('doctor_home')
            except Exception as e:
                messages.error(request, str(e))
    else:
        form = AvailabilityForm(doctor=request.user)

    return render(request, 'bookings/add_availability.html', {'form': form})


@login_required
def delete_availability(request, pk):
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied.')
        return redirect('home')

    availability = get_object_or_404(DoctorAvailability, pk=pk, doctor=request.user)

    if availability.is_booked:
        messages.error(request, 'Cannot delete a booked time slot.')
        return redirect('doctor_home')

    availability.delete()
    messages.success(request, 'Availability slot deleted successfully!')
    return redirect('doctor_home')


@login_required
def google_calendar_connect(request):
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied.')
        return redirect('home')
    redirect_uri = request.build_absolute_uri('/doctor/oauth2callback/')
    auth_url, state = get_google_auth_url(redirect_uri)
    request.session['oauth_state'] = state
    return redirect(auth_url)


@login_required
def oauth2callback(request):
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied.')
        return redirect('home')
    code = request.GET.get('code')
    if not code:
        messages.error(request, 'Authorization failed.')
        return redirect('doctor_home')
    try:
        redirect_uri = request.build_absolute_uri('/doctor/oauth2callback/')
        access_token, refresh_token = exchange_code_for_tokens(code, redirect_uri)
        profile = request.user.doctor_profile
        profile.google_calendar_token = access_token
        profile.google_refresh_token = refresh_token
        profile.save()
        messages.success(request, 'Google Calendar connected successfully!')
    except Exception as e:
        messages.error(request, f'Error connecting Google Calendar: {str(e)}')
    return redirect('doctor_home')
