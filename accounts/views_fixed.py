from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import UserProfile, Animal, HealthConsultation

# Custom Login View
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Ensure UserProfile exists
            profile, created = UserProfile.objects.get_or_create(user=user, defaults={'role': 'farmer'})
            
            # Redirect based on role
            if profile.role == 'doctor':
                return redirect('doctor_dashboard')
            else:
                return redirect('farmer_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

# Registration View
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        role = request.POST.get('role', 'farmer')
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user, role=role)
            login(request, user)
            if role == 'farmer':
                return redirect('farmer_dashboard')
            else:
                return redirect('doctor_dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

# Farmer Dashboard
@login_required
def farmer_dashboard(request):
    # Ensure profile exists
    profile, created = UserProfile.objects.get_or_create(user=request.user, defaults={'role': 'farmer'})
    
    if profile.role != 'farmer':
        return redirect('doctor_dashboard')

    animals = Animal.objects.filter(owner=request.user)
    consultations = HealthConsultation.objects.filter(farmer=request.user).order_by('-date')
    
    return render(request, 'dashboards/farmer.html', {
        'animals': animals,
        'consultations': consultations
    })

# Doctor Dashboard
@login_required
def doctor_dashboard(request):
    # Ensure profile exists
    profile, created = UserProfile.objects.get_or_create(user=request.user, defaults={'role': 'farmer'})
    
    if profile.role != 'doctor':
        return redirect('farmer_dashboard')
        
    cases = HealthConsultation.objects.filter(status='Pending').order_by('-date')
    return render(request, 'dashboards/doctor.html', {'cases': cases})

# Report Problem View
@login_required
def report_problem(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
    if request.method == "POST":
        symptoms = request.POST.get('symptoms')
        if symptoms:
            HealthConsultation.objects.create(
                farmer=request.user,
                animal=animal,
                symptoms=symptoms
            )
            return redirect('farmer_dashboard')
            
    return render(request, 'dashboards/report_problem.html', {'animal': animal})

# Logout View
def logout_view(request):
    logout(request)
    return redirect('login')
