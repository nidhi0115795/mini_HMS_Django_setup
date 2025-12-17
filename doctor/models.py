from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from accounts.models import User


class DoctorAvailability(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availabilities')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ['doctor', 'date', 'start_time', 'end_time']
        db_table = 'bookings_doctoravailability'
        managed = False

    def clean(self):
        if not self.doctor_id:
            return
        if getattr(self.doctor, 'role', None) != 'doctor':
            raise ValidationError('Only doctors can create availability slots.')
        if self.start_time >= self.end_time:
            raise ValidationError('End time must be after start time.')
        if self.date < timezone.now().date():
            raise ValidationError('Cannot create availability for past dates.')

    def __str__(self):
        return f"Dr. {self.doctor.username} - {self.date} {self.start_time}-{self.end_time}"


class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_bookings')
    availability = models.OneToOneField(DoctorAvailability, on_delete=models.CASCADE, related_name='booking')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    notes = models.TextField(blank=True)
    google_event_id_doctor = models.CharField(max_length=255, blank=True)
    google_event_id_patient = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'bookings_booking'
        managed = False

    def __str__(self):
        return f"{self.patient.username} with Dr. {self.doctor.username} on {self.availability.date}"
