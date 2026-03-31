from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum

from .forms import CustomUserCreationForm 
from .models import UserProfile, Animal, HealthConsultation, Production, DailyFarmDiary

def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        role = request.POST.get('role', 'farmer')
        if form.is_valid():
            user = form.save()
            UserProfile.objects.get_or_create(user=user, defaults={'role': role})
            login(request, user)
            return redirect('doctor_dashboard' if role == 'doctor' else 'farmer_dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

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

@login_required
def farmer_dashboard(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user, defaults={'role': 'farmer'})
    if profile.role != 'farmer': 
        return redirect('doctor_dashboard')
    
    if request.method == "POST" and 'add_animal' in request.POST:
        Animal.objects.create(
            owner=request.user,
            tag_id=request.POST.get('tag_id'),
            category=request.POST.get('category'),
            breed=request.POST.get('breed'),
            age=request.POST.get('age') or 0,
            weight=request.POST.get('weight') or 0
        )
        messages.success(request, "সফলভাবে যোগ করা হয়েছে।")
        return redirect('farmer_dashboard')

    animals = Animal.objects.filter(owner=request.user)
    consultations = HealthConsultation.objects.filter(farmer=request.user).order_by('-date')
    return render(request, 'dashboards/farmer.html', {
        'animals': animals, 
        'consultations': consultations,
        'profile': profile
    })

@login_required
def swit_report(request):
    if request.method == "POST":
        reg_id = request.POST.get('reg_id')
        sms_body = request.POST.get('sms_message')
        photo = request.FILES.get('animal_photo')

        if reg_id and sms_body:
            HealthConsultation.objects.create(
                farmer=request.user,
                animal_reg_id=reg_id,
                symptoms=sms_body,
                report_image=photo
            )
            messages.success(request, "ডাক্তারের কাছে SWIT রিপোর্ট পাঠানো হয়েছে!")
        else:
            messages.error(request, "আইডি এবং সমস্যার বিবরণ দিন।")
            
    return redirect('farmer_dashboard')

@login_required
def update_vaccine(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
    if request.method == "POST":
        v_date = request.POST.get('vaccine_date')
        animal.last_vaccination = v_date
        animal.save()
        
        HealthConsultation.objects.create(
            farmer=request.user,
            animal_reg_id=animal.tag_id,
            symptoms=f"Vaccination Update: Scheduled for {v_date}.",
            status='Pending'
        )
        messages.success(request, f"ID: {animal.tag_id} এর ভ্যাকসিন আপডেট হয়েছে।")
    return redirect('farmer_dashboard')

@login_required
def daily_diary_view(request):
    if request.method == "POST":
        DailyFarmDiary.objects.create(
            farmer=request.user,
            animal_sold_count=request.POST.get('animal_count') or 0,
            animal_sold_price=request.POST.get('animal_price') or 0,
            milk_liters=request.POST.get('milk_liters') or 0,
            milk_price=request.POST.get('milk_price') or 0,
            egg_count=request.POST.get('egg_count') or 0,
            egg_price=request.POST.get('egg_price') or 0,
            meat_kg=request.POST.get('meat_kg') or 0,
            meat_price=request.POST.get('meat_price') or 0,
            feed_cost=request.POST.get('feed_cost') or 0,
        )
        messages.success(request, "আজকের হিসাব সংরক্ষিত হয়েছে।")
        return redirect('daily_diary')

    last_week = timezone.now().date() - timedelta(days=7)
    weekly_data = DailyFarmDiary.objects.filter(farmer=request.user, date__gte=last_week)
    
    agg = weekly_data.aggregate(
        total_animal_price=Sum('animal_sold_price'),
        total_milk_price=Sum('milk_price'),
        total_egg_price=Sum('egg_price'),
        total_meat_price=Sum('meat_price'),
        total_exp=Sum('feed_cost')
    )
    
    total_income = (agg['total_animal_price'] or 0) + (agg['total_milk_price'] or 0) + \
                   (agg['total_egg_price'] or 0) + (agg['total_meat_price'] or 0)
    total_expense = agg['total_exp'] or 0
    
    history = DailyFarmDiary.objects.filter(farmer=request.user).order_by('-date')
    
    return render(request, 'dashboards/diary.html', {
        'history': history,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_profit': total_income - total_expense
    })

@login_required
def report_problem(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
    if request.method == "POST":
        symptoms = request.POST.get('symptoms')
        if symptoms:
            HealthConsultation.objects.create(
                farmer=request.user,
                animal_reg_id=animal.tag_id,
                symptoms=symptoms,
                status='Pending'
            )
            messages.success(request, "সমস্যাটি ডাক্তারের কাছে পাঠানো হয়েছে।")
    return redirect('farmer_dashboard')

@login_required
def milk_record(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
    if request.method == "POST":
        amount = request.POST.get('amount')
        if amount:
            Production.objects.create(animal=animal, milk_amount=amount)
            messages.success(request, "দুধের রেকর্ড সেভ করা হয়েছে।")
    return redirect('farmer_dashboard')

@login_required
def doctor_dashboard(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user, defaults={'role': 'doctor'})
    if profile.role != 'doctor': 
        return redirect('farmer_dashboard')
        
    pending_cases = HealthConsultation.objects.filter(status='Pending').order_by('-date')
    
    stats = {
        'pending': pending_cases.count(),
        'solved': HealthConsultation.objects.filter(status='Solved').count(),
        'total': HealthConsultation.objects.count(),
    }
    
    return render(request, 'dashboards/doctor.html', {
        'cases': pending_cases, 
        'profile': profile,
        'stats': stats
    })

@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'dashboards/profile.html', {'profile': profile})

@login_required
def add_prescription(request, case_id):
    case = get_object_or_404(HealthConsultation, id=case_id)
    if request.method == "POST":
        case.doctor_advice = request.POST.get('prescription')
        case.status = 'Solved'
        case.save()
        messages.success(request, "প্রেসক্রিপশন পাঠানো হয়েছে।")
    return redirect('doctor_dashboard')

def logout_view(request):
    logout(request)
    return redirect('login')