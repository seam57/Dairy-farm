import json
import google.generativeai as genai
from PIL import Image
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from .models import UserProfile, Animal, DailyFarmDiary, HealthConsultation
from decimal import Decimal

# --- Gemini AI Configuration ---
# API Key এখানে একবার কনফিগার করাই যথেষ্ট
genai.configure(api_key="AIzaSyAvEygVEFcON2Z4vz64ff6P8UykIVkRbJU")

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

@login_required
def daily_diary_view(request):
    if request.method == "POST":
        animal_id = request.POST.get('animal_id')
        animal_obj = Animal.objects.get(id=animal_id) if animal_id else None
        
        DailyFarmDiary.objects.create(
            farmer=request.user,
            animal=animal_obj,
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

    animal_stats = []
    for animal in animals:
        records = DailyFarmDiary.objects.filter(animal=animal)
        total_inc = sum(record.total_income for record in records)
        total_exp = sum(record.total_expense for record in records)
        net_prof = total_inc - total_exp
        
        animal_stats.append({
            'tag_id': animal.tag_id,
            'category': animal.get_category_display(),
            'income': total_inc,
            'expense': total_exp,
            'profit': net_prof,
        })

    last_7_days = history[:7][::-1]
    chart_dates = [record.date.strftime("%d %b") for record in last_7_days]
    chart_incomes = [float(record.total_income) for record in last_7_days]
    chart_expenses = [float(record.total_expense) for record in last_7_days]

    aggregate = history.aggregate(
        total_milk=Sum('milk_income'),
        total_meat=Sum('meat_income'),
        total_egg=Sum('egg_income')
    )
    pie_data = [
        float(aggregate['total_milk'] or 0),
        float(aggregate['total_meat'] or 0),
        float(aggregate['total_egg'] or 0)
    ]

    return render(request, 'dashboards/diary.html', {
        'history': history,
        'animals': animals,
        'animal_stats': animal_stats,
        'chart_dates': json.dumps(chart_dates),
        'chart_incomes': json.dumps(chart_incomes),
        'chart_expenses': json.dumps(chart_expenses),
        'pie_data': json.dumps(pie_data)
    })

# --- Updated AI Doctor View ---

@login_required
def farm_ai_doctor(request):
    response_text = ""
    if request.method == "POST":
        user_query = request.POST.get('user_query', '').strip()
        user_image = request.FILES.get('user_image')
        
        try:
            # মডেলের নাম সরাসরি ব্যবহার করুন
            model = genai.GenerativeModel('models/gemini-1.5-flash')
            
            system_prompt = (
                "তুমি একজন বিশেষজ্ঞ পশুচিকিৎসক। কৃষক তোমাকে কিছু প্রশ্ন করবে এবং সম্ভবত পশুর ছবি দেবে। "
                "তোমার কাজ হলো বাংলায় খুব সহজভাবে সম্ভাব্য রোগের নাম এবং প্রতিকার বলা। "
                "তবে অবশ্যই শেষে লিখে দেবে 'এটি একটি AI পরামর্শ, জরুরি প্রয়োজনে সরাসরি ডাক্তারের পরামর্শ নিন'।"
            )

            # ছবি থাকলে এবং প্রশ্ন থাকলে কন্টেন্ট সাজানো
            if user_image:
                img = Image.open(user_image)
                # ইমেজ ইনপুট হিসেবে পাঠালে লিস্ট আকারে পাঠাতে হয়
                response = model.generate_content([system_prompt, f"কৃষকের প্রশ্ন: {user_query}", img])
            else:
                # শুধু টেক্সট থাকলে
                response = model.generate_content(f"{system_prompt}\nকৃষকের প্রশ্ন: {user_query}")
            
            if response and response.text:
                response_text = response.text
            else:
                response_text = "AI কোনো উত্তর তৈরি করতে পারেনি। অনুগ্রহ করে আবার চেষ্টা করুন।"

        except Exception as e:
            # কারিগরি ভুলগুলো সঠিকভাবে ড্যাশবোর্ডে দেখানোর জন্য
            response_text = f"দুঃখিত, একটু সমস্যা হয়েছে। কারিগরি ত্রুটি: {str(e)}"

    return render(request, 'dashboards/farm_ai.html', {'response': response_text})

# --- Other Utility Views ---

@login_required
def update_vaccine(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
    if request.method == 'POST':
        v_date = request.POST.get('vaccine_date')
        if v_date:
            animal.last_vaccination_date = v_date
            animal.save()
    return redirect('farmer_dashboard')

@login_required
def doctor_dashboard(request):
    cases = HealthConsultation.objects.all().order_by('-date')
    return render(request, 'dashboards/doctor.html', {'cases': cases})

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')