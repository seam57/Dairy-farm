from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Animal, HealthConsultation, MilkProduction

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            profile, created = UserProfile.objects.get_or_create(user=user, defaults={'role': 'farmer'})
            return redirect('doctor_dashboard' if profile.role == 'doctor' else 'farmer_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def farmer_dashboard(request):
    try:
        if request.user.profile.role != 'farmer':
            return redirect('doctor_dashboard')
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=request.user, role='farmer')

    # পশু অ্যাড করার লজিক
    if request.method == "POST" and 'add_animal' in request.POST:
        Animal.objects.create(
            owner=request.user,
            tag_id=request.POST.get('tag_id'),
            breed=request.POST.get('breed'),
            age=request.POST.get('age'),
            weight=request.POST.get('weight')
        )
        return redirect('farmer_dashboard')

    animals = Animal.objects.filter(owner=request.user)
    consultations = HealthConsultation.objects.filter(farmer=request.user).order_by('-date')
    return render(request, 'dashboards/farmer.html', {'animals': animals, 'consultations': consultations})

@login_required
def report_problem(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
    if request.method == "POST":
        HealthConsultation.objects.create(
            farmer=request.user, animal=animal, symptoms=request.POST.get('symptoms')
        )
        return redirect('farmer_dashboard')
    return render(request, 'dashboards/report_problem.html', {'animal': animal})

def logout_view(request):
    logout(request)
    return redirect('login')