import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from decimal import Decimal

# আপনার মডেলগুলো ইমপোর্ট করা হচ্ছে
from .models import UserProfile, Animal, DailyFarmDiary, HealthConsultation, VaccinationRecord

# --- Gemini AI Configuration ---
load_dotenv()
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

# --- Farmer Dashboard ---
@login_required
def farmer_dashboard(request):
    if request.method == "POST" and 'add_animal' in request.POST:
        tag = request.POST.get('tag_id')
        cat = request.POST.get('category')
        brd = request.POST.get('breed')
        if tag and cat:
            Animal.objects.create(owner=request.user, tag_id=tag, category=cat, breed=brd)
            return redirect('farmer_dashboard')

    animals = Animal.objects.filter(owner=request.user)
    search_query = request.GET.get('search_id', '').strip()

    # শুরুতে হিস্ট্রি লিস্ট খালি থাকবে
    vaccination_history_list = []

    # শুধুমাত্র সার্চ বাটনে ক্লিক করলে ডাটা আসবে
    if search_query:
        vaccination_history_list = VaccinationRecord.objects.filter(
            animal__owner=request.user,
            animal__tag_id__iexact=search_query
        ).order_by('-date')

    # ── NEW: Dashboard summary card data ──
    vaccinated_count   = animals.filter(last_vaccination_date__isnull=False).count()
    unvaccinated_count = animals.filter(last_vaccination_date__isnull=True).count()
    total_diary_records = DailyFarmDiary.objects.filter(farmer=request.user).count()

    return render(request, 'dashboards/farmer.html', {
        'animals': animals,
        'vaccination_history_list': vaccination_history_list,
        'search_query': search_query,
        # NEW variables for summary cards
        'vaccinated_count': vaccinated_count,
        'unvaccinated_count': unvaccinated_count,
        'total_diary_records': total_diary_records,
    })


# --- Doctor Dashboard ---
@login_required
def doctor_dashboard(request):
    cases = HealthConsultation.objects.all().order_by('-date')
    return render(request, 'dashboards/doctor.html', {'cases': cases})


# --- Update Vaccine ---
@login_required
def update_vaccine(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
    if request.method == 'POST':
        vax_date = request.POST.get('vaccine_date')
        if vax_date:
            animal.last_vaccination_date = vax_date
            animal.save()
            VaccinationRecord.objects.create(animal=animal, date=vax_date)
    return redirect('farmer_dashboard')


# --- AI Diet Planner ---
@login_required
def diet_planner_view(request):
    response_text = ""
    target_animal = None
    if request.method == "POST":
        user_query = request.POST.get('user_query', '').strip()
        words = user_query.split()
        for word in words:
            animal_check = Animal.objects.filter(owner=request.user, tag_id__iexact=word).first()
            if animal_check:
                target_animal = animal_check
                break
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            animal_info = f"Type: {target_animal.category}, Breed: {target_animal.breed}" if target_animal else ""
            response = model.generate_content(f"Livestock Expert. Bangla. {animal_info} User Question: {user_query}")
            response_text = response.text
        except Exception as e:
            response_text = "AI সার্ভিস এখন ব্যস্ত।"
    return render(request, 'dashboards/diet_planner.html', {'response': response_text})


# --- AgroTrack/Diary ---
@login_required
def daily_diary_view(request):
    if request.method == "POST":
        if 'clear_agrotrack' in request.POST:
            DailyFarmDiary.objects.filter(farmer=request.user).delete()
            return redirect('daily_diary')
        else:
            animal_id = request.POST.get('animal_id')
            animal_obj = Animal.objects.filter(id=animal_id).first() if animal_id else None
            DailyFarmDiary.objects.create(
                farmer=request.user, animal=animal_obj,
                milk_income=request.POST.get('milk_income') or 0,
                meat_income=request.POST.get('meat_income') or 0,
                egg_income=request.POST.get('egg_income') or 0,
                feed_cost=request.POST.get('feed_cost') or 0,
                medicine_cost=request.POST.get('medicine_cost') or 0,
                other_cost=request.POST.get('other_cost') or 0
            )
            return redirect('daily_diary')

    history = DailyFarmDiary.objects.filter(farmer=request.user).order_by('-date')
    animals = Animal.objects.filter(owner=request.user)

    # চার্টের জন্য ডাটা — পুরনো logic ঠিক আছে
    history_asc = list(history.order_by('date'))
    chart_dates    = [r.date.strftime("%d %b") for r in history_asc]
    chart_incomes  = [float(r.total_income) for r in history_asc]
    chart_expenses = [float(r.total_expense) for r in history_asc]

    agg = history.aggregate(m=Sum('milk_income'), mt=Sum('meat_income'), e=Sum('egg_income'))
    pie_data = [float(agg['m'] or 0), float(agg['mt'] or 0), float(agg['e'] or 0)]

    # ── NEW: AgroTrack summary totals (মোট আয়, ব্যয়, নিট লাভ) ──
    totals = history.aggregate(
        ti=Sum('milk_income'),
        tm=Sum('meat_income'),
        te=Sum('egg_income'),
        tf=Sum('feed_cost'),
        tmed=Sum('medicine_cost'),
        to=Sum('other_cost')
    )
    total_income  = float((totals['ti'] or 0) + (totals['tm'] or 0) + (totals['te'] or 0))
    total_expense = float((totals['tf'] or 0) + (totals['tmed'] or 0) + (totals['to'] or 0))
    net_profit    = total_income - total_expense

    # ── NEW: Individual Animal ROI — পশু ভিত্তিক লাভ-ক্ষতি ──
    animal_stats = []
    for animal in animals:
        records = history.filter(animal=animal)
        if records.exists():
            agg_a = records.aggregate(
                mi=Sum('milk_income'), mt=Sum('meat_income'), ei=Sum('egg_income'),
                fc=Sum('feed_cost'),   mc=Sum('medicine_cost'), oc=Sum('other_cost')
            )
            income  = float((agg_a['mi'] or 0) + (agg_a['mt'] or 0) + (agg_a['ei'] or 0))
            expense = float((agg_a['fc'] or 0) + (agg_a['mc'] or 0) + (agg_a['oc'] or 0))
            profit  = income - expense
            category_display = {
                'cow': 'গরু', 'goat': 'ছাগল', 'hen': 'মুরগি', 'duck': 'হাঁস'
            }.get(animal.category, animal.category)
            animal_stats.append({
                'tag_id':   animal.tag_id,
                'category': category_display,
                'income':   income,
                'expense':  expense,
                'profit':   profit,
            })

    return render(request, 'dashboards/diary.html', {
        # পুরনো variables — ঠিক আছে
        'history':        history,
        'animals':        animals,
        'chart_dates':    json.dumps(chart_dates),
        'chart_incomes':  json.dumps(chart_incomes),
        'chart_expenses': json.dumps(chart_expenses),
        'pie_data':       json.dumps(pie_data),
        # NEW variables
        'animal_stats':   animal_stats,
        'total_income':   total_income,
        'total_expense':  total_expense,
        'net_profit':     net_profit,
    })


# --- AI Doctor ---
@login_required
def farm_ai_doctor(request):
    response_text = ""
    if request.method == "POST":
        user_query = request.POST.get('user_query', '').strip()
        user_image = request.FILES.get('user_image')
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            system_prompt = "You are a vet. Respond in Bangla."
            if user_image:
                img = Image.open(user_image)
                response = model.generate_content([system_prompt, user_query, img])
            else:
                response = model.generate_content(f"{system_prompt} {user_query}")
            response_text = response.text
        except:
            response_text = "AI সার্ভিস এখন বন্ধ।"
    return render(request, 'dashboards/farm_ai.html', {'response': response_text})


# --- Authentication ---
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
            UserProfile.objects.get_or_create(user=user, defaults={'role': 'farmer'})
            login(request, user)
            return redirect('farmer_dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        request.user.first_name = request.POST.get('full_name')
        request.user.save()
        profile.phone = request.POST.get('phone')
        profile.save()
        return redirect('profile_view')
    return render(request, 'accounts/profile.html', {'profile': profile})