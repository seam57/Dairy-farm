import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import UserProfile, Animal, DailyFarmDiary, HealthConsultation
from decimal import Decimal

@login_required
def farmer_dashboard(request):
    if request.method == "POST" and 'add_animal' in request.POST:
        tag = request.POST.get('tag_id')
        cat = request.POST.get('category')
        brd = request.POST.get('breed') # টেমপ্লেট থেকে Breed ইনপুট নেওয়া হচ্ছে
        
        if tag and cat:
            # Animal মডেলে breed ফিল্ড থাকায় এখন এটি সঠিকভাবে সেভ হবে
            Animal.objects.create(
                owner=request.user, 
                tag_id=tag, 
                category=cat, 
                breed=brd
            )
            return redirect('farmer_dashboard')

    animals = Animal.objects.filter(owner=request.user)
    consultations = HealthConsultation.objects.filter(farmer=request.user).order_by('-date')
    return render(request, 'dashboards/farmer.html', {
        'animals': animals, 
        'consultations': consultations
    })

@login_required
def update_vaccine(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
    if request.method == 'POST':
        v_date = request.POST.get('vaccine_date')
        if v_date:
            animal.last_vaccination_date = v_date
            animal.save()
            return redirect('farmer_dashboard')
    return redirect('farmer_dashboard')

@login_required
def daily_diary_view(request):
    if request.method == "POST":
        animal_id = request.POST.get('animal_id')
        DailyFarmDiary.objects.create(
            farmer=request.user,
            animal_id=animal_id if animal_id else None,
            milk_income=Decimal(request.POST.get('milk_income') or 0),
            meat_income=Decimal(request.POST.get('meat_income') or 0),
            egg_income=Decimal(request.POST.get('egg_income') or 0),
            feed_cost=Decimal(request.POST.get('feed_cost') or 0),
            medicine_cost=Decimal(request.POST.get('medicine_cost') or 0),
            other_cost=Decimal(request.POST.get('other_cost') or 0),
        )
        return redirect('daily_diary')

    diary_records = DailyFarmDiary.objects.filter(farmer=request.user).order_by('date')
    dates = [d.date.strftime("%d %b") for d in diary_records]
    incomes = [d.total_income for d in diary_records]
    expenses = [d.total_expense for d in diary_records]

    totals = diary_records.aggregate(
        total_milk=Sum('milk_income'),
        total_meat=Sum('meat_income'),
        total_egg=Sum('egg_income')
    )

    context = {
        'animals': Animal.objects.filter(owner=request.user, is_active=True),
        'history': diary_records.reverse()[:10],
        'chart_dates': json.dumps(dates),
        'chart_incomes': json.dumps(incomes),
        'chart_expenses': json.dumps(expenses),
        'pie_data': json.dumps([
            float(totals['total_milk'] or 0),
            float(totals['total_meat'] or 0),
            float(totals['total_egg'] or 0)
        ]),
    }
    return render(request, 'dashboards/diary.html', context)

@login_required
def milk_record(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
    return redirect('farmer_dashboard')

@login_required
def doctor_dashboard(request):
    cases = HealthConsultation.objects.order_by('-date')
    stats = {
        'total': cases.count(),
        'pending': cases.filter(status__iexact='Pending').count(),
        'solved': cases.exclude(status__iexact='Pending').count(),
    }
    return render(request, 'dashboards/doctor.html', {'cases': cases, 'stats': stats})

@login_required
def report_problem(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
    if request.method == 'POST':
        HealthConsultation.objects.create(
            farmer=request.user,
            animal_reg_id=animal.tag_id,
            symptoms=request.POST.get('symptoms', ''),
            status='Pending'
        )
        return redirect('farmer_dashboard')
    return render(request, 'dashboards/report_problem.html', {'animal': animal})

@login_required
def swit_report(request):
    if request.method == 'POST':
        HealthConsultation.objects.create(
            farmer=request.user,
            animal_reg_id=request.POST.get('reg_id', ''),
            symptoms=request.POST.get('sms_message', ''),
            status='Pending'
        )
    return redirect('farmer_dashboard')

@login_required
def add_prescription(request, case_id):
    case = get_object_or_404(HealthConsultation, id=case_id)
    if request.method == 'POST':
        case.status = 'Resolved'
        case.save(update_fields=['status'])
    return redirect('doctor_dashboard')

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('farmer_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user, role='farmer')
            login(request, user)
            return redirect('farmer_dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')