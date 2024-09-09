from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from datetime import time, timedelta, datetime, date
from django.core.exceptions import ValidationError

from .models import *

class RegistrationForm(UserCreationForm):
    #prebuild form in django - UserCreationForm
    identity_no =  forms.CharField(max_length=20, help_text='Required to add your identity number')

    class Meta:
        model = AppUser
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'dob', 'identity_no', 'blood_group', 'gender', 'password1', 'password2']


class AuthenticationForm(forms.ModelForm):
    #here we are extending forms from models 

    password = forms.CharField(label = 'Password', widget = forms.PasswordInput) #widget here identifies password input and doesn't allow password to be shown

    class Meta:
        model = AppUser
        fields =  ('identity_no', 'password')

    #def clean can be used in modelform --> executes clean method before forms get processed. checks form input validity
    def clean(self):
        identity_no = self.cleaned_data['identity_no']
        password = self.cleaned_data['password']
        if not authenticate (identity_no=identity_no, password=password):
            raise forms.ValidationError("Invalid Login") # non-field error. Error that's not particular to any fields
        


# Helper function to generate time slots
def generate_time_slots(start_time, end_time, interval):
    time_slots = []
    current_time = start_time
    while current_time <= end_time:
        time_slots.append((current_time.strftime('%H:%M'), current_time.strftime('%I:%M %p')))
        current_time = (datetime.combine(date.today(), current_time) + interval).time()
    return time_slots



class AppointmentForm(forms.ModelForm):
    # Custom validation for appointment_date
    appointment_date = forms.DateField(
        widget=forms.SelectDateWidget(),
        initial=date.today() + timedelta(days=1),  # Default initial value is tomorrow
    )

    TIME_CHOICES = generate_time_slots(time(10, 0), time(18, 0), timedelta(minutes=30))  # From 10:00 AM to 6:00 PM

    appointment_time = forms.ChoiceField(choices=TIME_CHOICES)

    class Meta:
        model = Appointment
        fields = ['center', 'appointment_date', 'appointment_time', 'notes']

    def clean_appointment_date(self):
        appointment_date = self.cleaned_data.get('appointment_date')

        # Check if the selected date is in the past
        if appointment_date <= date.today():
            raise ValidationError("You cannot select a past date. Please select a future date.")

        return appointment_date


class EligibilityQuizForm(forms.Form):
    current_question = forms.IntegerField(widget=forms.HiddenInput(), initial=1)
    answer = forms.ChoiceField(choices=[('yes', 'Yes'), ('no', 'No')], widget=forms.RadioSelect)



