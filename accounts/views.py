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
from .models import UserProfile, Animal, DailyFarmDiary, HealthConsultation
from decimal import Decimal

# --- Load Environment Variables ---
load_dotenv()

# --- Gemini AI Configuration ---
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

# --- Authentication Views ---
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
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

# --- Dashboard Views ---
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
    vaccination_history_list = Animal.objects.filter(owner=request.user, last_vaccination_date__isnull=False)
    
    if search_query:
        vaccination_history_list = vaccination_history_list.filter(tag_id__iexact=search_query)
    
    vaccination_history_list = vaccination_history_list.order_by('-last_vaccination_date')

    return render(request, 'dashboards/farmer.html', {
        'animals': animals,
        'vaccination_history_list': vaccination_history_list,
        'search_query': search_query,
    })

# --- AI Diet Planner (Your Original Logic) ---
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
            model = genai.GenerativeModel('gemini-1.5-flash') # Stable model
            animal_info = f"Animal Type: {target_animal.get_category_display()}, Breed: {target_animal.breed}, ID: {target_animal.tag_id}." if target_animal else "General advice."
            system_prompt = f"Expert livestock nutritionist. Answer in Bangla. User query info: {animal_info}"
            response = model.generate_content(f"{system_prompt}\nUser Question: {user_query}")
            response_text = response.text
        except Exception as e:
            response_text = f"Error: {str(e)}"
    return render(request, 'dashboards/diet_planner.html', {'response': response_text})

# --- Daily Diary (Graph Fix & Functional) ---
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
                milk_income=request.POST.get('milk_income') or 0, meat_income=request.POST.get('meat_income') or 0,
                egg_income=request.POST.get('egg_income') or 0, feed_cost=request.POST.get('feed_cost') or 0,
                medicine_cost=request.POST.get('medicine_cost') or 0, other_cost=request.POST.get('other_cost') or 0
            )
            return redirect('daily_diary')

    history_asc = DailyFarmDiary.objects.filter(farmer=request.user).order_by('date')
    history_desc = history_asc.order_by('-date')
    animals = Animal.objects.filter(owner=request.user)

    # Graph Data Preparation
    chart_dates = [r.date.strftime("%d %b") for r in history_asc]
    chart_incomes = [float(r.total_income) for r in history_asc]
    chart_expenses = [float(r.total_expense) for r in history_asc]

    agg = history_asc.aggregate(m=Sum('milk_income'), mt=Sum('meat_income'), e=Sum('egg_income'))
    pie_data = [float(agg['m'] or 0), float(agg['mt'] or 0), float(agg['e'] or 0)]

    return render(request, 'dashboards/diary.html', {
        'history': history_desc, 'animals': animals,
        'chart_dates': json.dumps(chart_dates), 'chart_incomes': json.dumps(chart_incomes),
        'chart_expenses': json.dumps(chart_expenses), 'pie_data': json.dumps(pie_data)
    })

# --- AI Doctor (Your Full Original Logic with Image) ---
@login_required
def farm_ai_doctor(request):
    response_text = ""
    if request.method == "POST":
        user_query = request.POST.get('user_query', '').strip()
        user_image = request.FILES.get('user_image')
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            system_prompt = "You are an expert veterinarian. Respond in simple Bengali. Identify disease and suggest care. End with: 'এটি AI পরামর্শ, প্রয়োজনে ডাক্তার দেখান।'"
            if user_image:
                img = Image.open(user_image)
                response = model.generate_content([system_prompt, f"Question: {user_query}", img])
            else:
                response = model.generate_content(f"{system_prompt}\nQuestion: {user_query}")
            response_text = response.text
        except Exception as e:
            # Fallback for Quota or Technical error
            query_lower = user_query.lower()
            if "jor" in query_lower or "fever" in query_lower:
                response_text = "জ্বরের জন্য: পশুকে ঠান্ডা জায়গায় রাখুন এবং ডাক্তার দেখান।"
            else:
                response_text = "দৈনিক কোটা শেষ। জরুরি প্রয়োজনে পশু চিকিৎসকের পরামর্শ নিন।"
    return render(request, 'dashboards/farm_ai.html', {'response': response_text, 'user_query': request.POST.get('user_query', '')})

# --- Profile, Doctor & Vaccine Functions ---
@login_required
def doctor_dashboard(request):
    cases = HealthConsultation.objects.all().order_by('-date')
    return render(request, 'dashboards/doctor.html', {'cases': cases})

@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        request.user.first_name = request.POST.get('full_name')
        request.user.save()
        profile.phone = request.POST.get('phone'); profile.location = request.POST.get('location'); profile.save()
        return redirect('profile_view')
    return render(request, 'accounts/profile.html', {'profile': profile})

@login_required
def update_vaccine(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
    if request.method == 'POST':
        animal.last_vaccination_date = request.POST.get('vaccine_date')
        animal.save()
    return redirect('farmer_dashboard')