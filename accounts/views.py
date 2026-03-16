from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages

# আপনার কাস্টম ফর্ম এবং মডেল ইমপোর্ট
from .forms import CustomUserCreationForm 
from .models import UserProfile, Animal, HealthConsultation, Production, Vaccination

# --- Registration View ---
def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        role = request.POST.get('role', 'farmer')
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user, role=role)
            login(request, user)
            return redirect('doctor_dashboard' if role == 'doctor' else 'farmer_dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

# --- Login View ---
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'role': 'farmer'})
            return redirect('doctor_dashboard' if profile.role == 'doctor' else 'farmer_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

# --- Farmer Dashboard ---
@login_required
def farmer_dashboard(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user, defaults={'role': 'farmer'})
    if profile.role != 'farmer': 
        return redirect('doctor_dashboard')
    
    # নতুন পশু যোগ করার লজিক
    if request.method == "POST" and 'add_animal' in request.POST:
        Animal.objects.create(
            owner=request.user,
            tag_id=request.POST.get('tag_id'),
            category=request.POST.get('category'), # cow, goat, hen, etc.
            breed=request.POST.get('breed'),
            age=request.POST.get('age') or 0,
            weight=request.POST.get('weight') or 0
        )
        messages.success(request, "নতুন পশু/পাখি সফলভাবে যোগ করা হয়েছে।")
        return redirect('farmer_dashboard')

    animals = Animal.objects.filter(owner=request.user)
    consultations = HealthConsultation.objects.filter(farmer=request.user).order_by('-date')
    return render(request, 'dashboards/farmer.html', {
        'animals': animals, 
        'consultations': consultations,
        'profile': profile
    })

# --- Vaccination Update (আপনার নকশা অনুযায়ী নতুন যোগ করা হয়েছে) ---
@login_required
def update_vaccine(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
    if request.method == "POST":
        v_date = request.POST.get('vaccine_date')
        animal.last_vaccination = v_date
        animal.save()
        
        # ডাক্তারকে রিপোর্ট পাঠানোর জন্য অটো-কনসালটেশন তৈরি
        HealthConsultation.objects.create(
            farmer=request.user,
            animal=animal,
            symptoms=f"Vaccination Update: Scheduled for {v_date}. Please review health status.",
            status='Pending'
        )
        messages.success(request, f"ID: {animal.tag_id} এর ভ্যাকসিনের তারিখ আপডেট হয়েছে এবং ডাক্তারকে জানানো হয়েছে।")
    return redirect('farmer_dashboard')

# --- Report Problem View ---
@login_required
def report_problem(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
    if request.method == "POST":
        symptoms = request.POST.get('symptoms')
        if symptoms:
            HealthConsultation.objects.create(
                farmer=request.user,
                animal=animal,
                symptoms=symptoms,
                status='Pending'
            )
            messages.success(request, "সমস্যাটি ডাক্তারের কাছে পাঠানো হয়েছে।")
            return redirect('farmer_dashboard')
    return render(request, 'dashboards/report_problem.html', {'animal': animal})

# --- Doctor Dashboard ---
@login_required
def doctor_dashboard(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user, defaults={'role': 'doctor'})
    if profile.role != 'doctor': 
        return redirect('farmer_dashboard')
        
    cases = HealthConsultation.objects.filter(status='Pending').order_by('-date')
    return render(request, 'dashboards/doctor.html', {
        'cases': cases, 
        'profile': profile
    })

# --- Profile View ---
@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        request.user.email = request.POST.get('email')
        request.user.save()
        messages.success(request, "আপনার প্রোফাইল সফলভাবে আপডেট করা হয়েছে!")
        return redirect('profile_view')
    return render(request, 'dashboards/profile.html', {'profile': profile})

# --- Doctor Actions ---
@login_required
def add_prescription(request, case_id):
    case = get_object_or_404(HealthConsultation, id=case_id)
    if request.method == "POST":
        case.doctor_advice = request.POST.get('prescription') # models.py এর সাথে মিল রেখে
        case.status = 'Solved'
        case.save()
        messages.success(request, "প্রেসক্রিপশন পাঠানো হয়েছে।")
    return redirect('doctor_dashboard')

# --- Milk/Egg Production Record ---
@login_required
def milk_record(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
    if request.method == "POST":
        amount = request.POST.get('amount')
        if amount:
            # Cow/Goat হলে দুধে, অন্যথায় ডিমে কাউন্ট হবে
            if animal.category in ['cow', 'goat']:
                Production.objects.create(animal=animal, milk_amount=amount)
            else:
                Production.objects.create(animal=animal, egg_count=amount)
            messages.success(request, "রেকর্ড সেভ করা হয়েছে।")
    return redirect('farmer_dashboard')

# --- Logout ---
def logout_view(request):
    logout(request)
    return redirect('login')