from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Sum
from .models import UserProfile, Animal, HealthConsultation, DailyFarmDiary

# ১. লগইন ভিউ
@require_http_methods(["GET", "POST"])
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

# ২. রেজিস্ট্রেশন ভিউ
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        role = request.POST.get('role', 'farmer')
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user, role=role)
            login(request, user)
            return redirect('farmer_dashboard' if role == 'farmer' else 'doctor_dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

# ৩. ফার্মার ড্যাশবোর্ড
@login_required
def farmer_dashboard(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user, defaults={'role': 'farmer'})
    if profile.role != 'farmer':
        return redirect('doctor_dashboard')
    animals = Animal.objects.filter(owner=request.user)
    consultations = HealthConsultation.objects.filter(farmer=request.user).order_by('-date')
    return render(request, 'dashboards/farmer.html', {'animals': animals, 'consultations': consultations})

# ৪. স্মার্ট ডায়েরি ভিউ (এটিই আপনার এরর ফিক্স করবে)
@login_required
def daily_diary_view(request):
    if request.method == "POST":
        category = request.POST.get('category')
        income = request.POST.get('income_amount', 0)
        feed = request.POST.get('feed_cost', 0)
        vaccine = request.POST.get('vaccine_cost', 0)
        
        DailyFarmDiary.objects.create(
            farmer=request.user,
            category=category,
            income_amount=income,
            feed_cost=feed,
            vaccine_cost=vaccine
        )
        return redirect('daily_diary_view')

    history = DailyFarmDiary.objects.filter(farmer=request.user).order_by('-date')
    
    # এরর এড়াতে Sum ব্যবহার করে হিসাব করা (৯৫ নম্বর লাইনের সমস্যা সমাধান)
    total_income = sum(record.total_daily_income for record in history)
    total_expense = sum(record.total_daily_expense for record in history)
    net_profit = total_income - total_expense

    # AI Prediction Logic
    prediction = {
        'cows': int(net_profit // 50000) if net_profit > 0 else 0,
        'goats': int(net_profit // 10000) if net_profit > 0 else 0,
        'hens': int(net_profit // 500) if net_profit > 0 else 0,
    }

    return render(request, 'dashboards/diary.html', {
        'history': history,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_profit': net_profit,
        'prediction': prediction
    })

# ৫. প্রোফাইল ভিউ (NoReverseMatch সমাধান করবে)
@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})

# ৬. লগআউট ভিউ
def logout_view(request):
    logout(request)
    return redirect('login_view')