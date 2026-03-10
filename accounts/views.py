from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm
from .models import Animal, HealthConsultation, Profile


def home(request):
    return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    auth_logout(request)
    return redirect('login')


@login_required
def dashboard_redirect(request):
    try:
        
        role = request.user.profile.role
        if role == 'farmer':
            return redirect('farmer_dashboard')
        elif role == 'doctor':
            return redirect('doctor_dashboard')
    except Profile.DoesNotExist:
        return redirect('home')
    return redirect('home')


@login_required
def farmer_dashboard(request):
    
    profile = request.user.profile 
    animals = Animal.objects.filter(owner=request.user)
    
    context = {
        'profile': profile,
        'animals': animals,
    }
    return render(request, 'dashboards/farmer.html', context)


@login_required
def doctor_dashboard(request):
    
    reports = HealthConsultation.objects.filter(status='pending')
    return render(request, 'dashboards/doctor.html', {'reports': reports})


@login_required
def report_problem(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
    if request.method == "POST":
        note = request.POST.get('note')
        HealthConsultation.objects.create(animal=animal, farmer_note=note)
        return redirect('farmer_dashboard')
    return render(request, 'dashboards/report_problem.html', {'animal': animal})