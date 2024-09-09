from django.shortcuts import render,redirect
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.timezone import now  #gets current date and time
import requests
from .forms import *
from .models import *


def home(request):
    blood_inventory = BloodInventory.objects.all()
    return render(request, 'blood_bank_app/homepage.html', {'blood_inventory': blood_inventory})

def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

def registration_view(request):
    context={}
    if request.POST:
        form =  RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            identity_no = form.cleaned_data.get('identity_no')
            raw_password= form.cleaned_data.get('password1')
            user =  authenticate (identity_no= identity_no, password = raw_password)
            login(request,user)
            return redirect('home')
        else:
            context['registration_form'] = form 

    else:
        form = RegistrationForm()
        context['registration_form'] =form
    return render (request, 'blood_bank_app/register.html', context)


def logout_view(request):
    logout(request)
    return redirect('home')

def login_view(request):

    context = {}

    user = request.user
    if user.is_authenticated: #if user is already logged in
        return redirect('home')
    
    if request.POST :
        form = AuthenticationForm(request.POST)
        if form.is_valid ():
            identity_no = request.POST['identity_no']
            password = request.POST['password']
            user= authenticate(identity_no=identity_no, password=password)

            #if login form is validated and authenticated, log them in 
            if user: 
                login(request, user)
                return redirect("home")
            
    else:
        form = AuthenticationForm()


    context ['login_form'] = form 
    return render (request, 'blood_bank_app/login.html', context)




@login_required
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.donor = request.user  # Set the current user as the donor
            appointment.save()

            # Store appointment details in the session for the success page
            request.session['appointment_date'] = form.cleaned_data.get('appointment_date').strftime('%Y-%m-%d')
            request.session['appointment_time'] = form.cleaned_data.get('appointment_time')
            request.session['appointment_center'] = appointment.center.name 

            return redirect('appointment_success')  # Redirect to a success page
    else:
        form = AppointmentForm()
    
    return render(request, 'blood_bank_app/book_appointment.html', {'form': form})


@login_required
def appointment_success(request):
    return render(request, 'blood_bank_app/appointment_success.html')


def dashboard(request):
    # Default view can show user profile or appointment list based on a GET parameter
    section = request.GET.get('section', 'profile')  # 'profile' is the default section

    if section == 'profile':
        return render(request, 'blood_bank_app/user_dashboard.html', {'section': 'profile'})
    elif section == 'appointments':
        # Get current date and time
        current_date = now().date()

        # Separate past and future appointments
        past_appointments = Appointment.objects.filter(donor=request.user, appointment_date__lt=current_date)
        future_appointments = Appointment.objects.filter(donor=request.user, appointment_date__gte=current_date)

        return render(request, 'blood_bank_app/user_dashboard.html', {
            'section': 'appointments',
            'past_appointments': past_appointments,
            'future_appointments': future_appointments,
        })
    else:
        return render(request, 'blood_bank_app/user_dashboard.html', {'section': 'profile'})



QUESTIONS = [
    {
        "question": "Are you 16 - 60 years old?",
        "yes_message": None,
        "no_message": "Sorry, you need to be at least 16 to donate blood."
    },
    {
        "question": "Are you above 45kg?",
        "yes_message": None,
        "no_message": "Sorry! You have to be at least 45kg to donate blood."
    },
    {
        "question": "Are you generally in good health? (No symptoms of infection for at least one week)",
        "yes_message": None,
        "no_message": "Sorry! You need to be in good health to donate blood."
    },
    {
        "question": "Have you visited or lived in the United Kingdom between 1980 and 1996 for a cumulative period of 3 months or longer?",
        "yes_message": "Sorry! You are not eligible to donate blood at the moment.",
        "no_message": None
    },
    {
        "question": "Are you experiencing heavy menstrual flow or cramps? Are you pregnant or breastfeeding?",
        "yes_message": "Sorry! You are not eligible to donate blood at the moment.",
        "no_message": None
    },
    {
        "question": "Have you done dental work recently?",
        "yes_message": "Sorry! You are not eligible to donate blood at the moment.",
        "no_message": None
    },
    {
        "question": "Have you taken herbal supplements or traditional herbal remedies recently?",
        "yes_message": "Sorry! You are not eligible to donate blood at the moment.",
        "no_message": None
    },
    {
        "question": "Have you had a piercing or a tattoo recently, done with non-disposable needles?",
        "yes_message": "Sorry! You are not eligible to donate blood at the moment.",
        "no_message": None
    },
    {
        "question": "Do you have diabetes or hypertension for which you are taking more than a single medication?",
        "yes_message": "Sorry! You are not eligible to donate blood at the moment.",
        "no_message": None
    },
    {
        "question": "Have you travelled overseas to a malaria endemic area in the past 4 months?",
        "yes_message": "Sorry! You are not eligible to donate blood at the moment.",
        "no_message": None
    },
]

def eligibility_quiz(request):
    form = EligibilityQuizForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        current_question = form.cleaned_data['current_question']
        answer = form.cleaned_data['answer']
        question_data = QUESTIONS[current_question - 1]

        # Handle incorrect answers (i.e., show error message)
        if (answer == 'no' and question_data['no_message'] is not None) or (answer == 'yes' and question_data['yes_message'] is not None):
            error_message = question_data['no_message'] if answer == 'no' else question_data['yes_message']
            return render(request, 'blood_bank_app/eligibility_quiz.html', {
                'form': form,
                'current_question': current_question,
                'error_message': error_message,
                'failed': True,
                'question_data': question_data,
                'total_questions': len(QUESTIONS),
            })

        # If the answer passes (no error), move to the next question
        if current_question < len(QUESTIONS):
            # Increment current question and render the next question
            next_question = current_question + 1
            form = EligibilityQuizForm(initial={'current_question': next_question})  # Keep the incremented question number
            return render(request, 'blood_bank_app/eligibility_quiz.html', {
                'form': form,
                'current_question': next_question,
                'question_data': QUESTIONS[next_question - 1],  # Fetch the next question
                'total_questions': len(QUESTIONS),
            })

        # Success case when all questions are completed
        else:
            return render(request, 'blood_bank_app/eligibility_quiz.html', {
                'form': None,
                'success_message': "Yes! You Can Be A Blood Hero! You are eligible to donate blood! You can book appointment here "
            })

    # Initial GET request or invalid form case
    else:
        current_question = 1
        form = EligibilityQuizForm(initial={'current_question': current_question})

    return render(request, 'blood_bank_app/eligibility_quiz.html', {
        'form': form,
        'current_question': current_question,
        'question_data': QUESTIONS[current_question - 1],
        'total_questions': len(QUESTIONS),
    })



def blood_inventory_view(request):

    blood_inventory = BloodInventory.objects.all()
    print(blood_inventory)
    return render(request, 'blood_bank_app/blood_inventory_dashboard.html', {'blood_inventory': blood_inventory})


def donation_centers_view(request):
    print("location View is being called")  # Add this for debugging
    donation_centers = DonationCenter.objects.all()
    return render(request, 'blood_bank_app/locations.html', {'donation_centers': donation_centers})


def why_donate_view(request):
    return render(request, 'blood_bank_app/why_donate.html')


def blood_types_view(request):
    return render(request, 'blood_bank_app/blood_types.html')

def who_are_we_views(request):
    return render(request, 'blood_bank_app/who_are_we.html')



def rewards_board(request):
    bronze_members = AppUser.objects.filter(membership_level='bronze')
    silver_members = AppUser.objects.filter(membership_level='silver')
    gold_members = AppUser.objects.filter(membership_level='gold')
    platinum_members = AppUser.objects.filter(membership_level='platinum')

    return render(request, 'blood_bank_app/rewards_board.html', {
        'bronze_members': bronze_members,
        'silver_members': silver_members,
        'gold_members': gold_members,
        'platinum_members': platinum_members,
    })
    






    