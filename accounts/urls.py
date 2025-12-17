from django.urls import path
from . import views

urlpatterns = [
    path('signup/patient/',views.patient_signup, name='patient_signup'),
    path('signup/doctor/',views.doctor_signup, name='doctor_signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    
]