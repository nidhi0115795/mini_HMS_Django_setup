from django import forms
from .models import DoctorAvailability, Booking
from django.utils import timezone


class AvailabilityForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date()}))
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = DoctorAvailability
        fields = ['date', 'start_time', 'end_time']

    def __init__(self, *args, **kwargs):
        self.doctor = kwargs.pop('doctor', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        availability = super().save(commit=False)
        if self.doctor:
            availability.doctor = self.doctor
        if commit:
            availability.save()
        return availability


class BookingForm(forms.ModelForm):
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = Booking
        fields = ['notes']
