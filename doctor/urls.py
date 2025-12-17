from django.urls import path
from .views import (
    dashboard,
    add_availability,
    delete_availability,
    google_calendar_connect,
    oauth2callback,
)

urlpatterns = [
    path('', dashboard, name='doctor_home'),
    path('add-availability/', add_availability, name='doctor_add_availability'),
    path('delete-availability/<int:pk>/', delete_availability, name='doctor_delete_availability'),
    path('google-calendar/connect/', google_calendar_connect, name='doctor_google_calendar_connect'),
    path('oauth2callback/', oauth2callback, name='doctor_oauth2callback'),
]
