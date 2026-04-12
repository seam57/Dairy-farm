import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
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
            # মডেলের নাম আপনার আগের কোড অনুযায়ী রাখা হলো
            model = genai.GenerativeModel('gemini-2.5-flash')
            if target_animal:
                animal_info = f"Animal Type: {target_animal.get_category_display()}, Breed: {target_animal.breed}, ID: {target_animal.tag_id}."
            else:
                animal_info = "Specific animal ID not found in database, give general advice."


            system_prompt = (
                f"Tumi ekjon expert livestock nutritionist. User query: {animal_info} "
                "User Bangla, English ba Banglish mixed vabe question korte pare. "
                "Tumi tader somossa bujhe Banglay ekta su-somo khabrer chart (Diet Plan) dibe. "
                "Chart ti table ba list akare sundor vabe dekhabe."
            )


            response = model.generate_content(f"{system_prompt}\nUser Question: {user_query}")
            response_text = response.text if response and response.text else "AI kono uttor dity pareni."


        except Exception as e:
            response_text = f"Technical Error: {str(e)}"


    return render(request, 'dashboards/diet_planner.html', {'response': response_text})


# --- Dairy View ---


@login_required
def daily_diary_view(request):
    if request.method == "POST":
        if 'clear_agrotrack' in request.POST:
            # Clear all diary records for the user
            DailyFarmDiary.objects.filter(farmer=request.user).delete()
            return redirect('daily_diary')
        else:
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


# --- AI Doctor (আপনার অরিজিনাল লজিক) ---


@login_required
def farm_ai_doctor(request):
    response_text = ""
    if request.method == "POST":
        user_query = request.POST.get('user_query', '').strip()
        user_image = request.FILES.get('user_image')
       
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            system_prompt = (
                "You are an expert veterinarian. The user will describe their animal's symptoms or problems in Bengali, English, or mixed language. "
                "Respond in simple, clear Bengali. "
                "First, try to identify the possible disease or condition based on the symptoms described. "
                "Then, provide practical treatment advice, including home remedies if appropriate, and when to seek professional help. "
                "Always end your response with: 'এটি AI পরামর্শ, প্রয়োজনে ডাক্তার দেখান।' (This is AI advice, consult a doctor if necessary.) "
                "Be helpful, accurate, and emphasize that this is not a substitute for professional veterinary care."
            )


            if user_image:
                img = Image.open(user_image)
                response = model.generate_content([system_prompt, f"Question: {user_query}", img])
            else:
                response = model.generate_content(f"{system_prompt}\nQuestion: {user_query}")
           
            response_text = response.text if response and response.text else "AI error."
        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "quota" in error_str or "resource exhausted" in error_str:
                # Provide general advice based on keywords in user_query
                query_lower = user_query.lower()
                advice = ""
                if "jor" in query_lower or "fever" in query_lower or "temperature" in query_lower:
                    advice = "জ্বরের জন্য: পশুকে ঠান্ডা জায়গায় রাখুন, পর্যাপ্ত পানি দিন, এবং যদি জ্বর না কমে তাহলে ডাক্তার দেখান। (For fever: Keep the animal in a cool place, provide plenty of water, and consult a doctor if fever doesn't subside.)"
                elif "khokha" in query_lower or "cough" in query_lower:
                    advice = "খোকার জন্য: পরিষ্কার পরিবেশ নিশ্চিত করুন, ধূমপান এড়িয়ে চলুন, এবং প্রয়োজনে এন্টিবায়োটিক দিন। (For cough: Ensure clean environment, avoid smoke, and give antibiotics if necessary.)"
                elif "diarrhea" in query_lower or "amashay" in query_lower or "পেটের সমস্যা" in query_lower:
                    advice = "পেটের সমস্যার জন্য: ইলেক্ট্রোলাইট দিন, নরম খাবার খাওয়ান, এবং ডাক্তারের পরামর্শ নিন। (For stomach issues: Give electrolytes, feed soft food, and consult a doctor.)"
                elif "skin" in query_lower or "charma" in query_lower or "rash" in query_lower:
                    advice = "চামড়ার সমস্যার জন্য: পরিষ্কার রাখুন, এন্টিফাঙ্গাল ক্রিম ব্যবহার করুন, এবং ডাক্তার দেখান। (For skin issues: Keep clean, use antifungal cream, and consult a doctor.)"
                else:
                    advice = "সাধারণ পরামর্শ: আপনার পশুর সমস্যা সম্পর্কে চিন্তিত? অনুগ্রহ করে একজন প্রকৃত পশু চিকিৎসকের সাথে যোগাযোগ করুন। পশুদের সুস্থ রাখার জন্য: পরিষ্কার পানি প্রদান করুন, ভারসাম্যপূর্ণ খাবার দিন, নিয়মিত চেকআপ করান। (General advice: Consult a real veterinarian. Keep animals healthy with clean water, balanced diet, regular checkups.)"
                
                response_text = f"আপনার দৈনিক কোটা শেষ হয়ে গেছে। তাই AI এখন সাধারণ পরামর্শ দিচ্ছে:\n\n{advice}\n\n(Quota exceeded. Providing general advice based on your query.)"
            else:
                response_text = f"Technical Error: {str(e)}"


    return render(request, 'dashboards/farm_ai.html', {
        'response': response_text,
        'user_query': request.POST.get('user_query', '').strip() if request.method == "POST" else ""
    })


# --- Missing Functions Added (Keep URLs working) ---


@login_required
def doctor_dashboard(request):
    cases = HealthConsultation.objects.all().order_by('-date')
    return render(request, 'dashboards/doctor.html', {'cases': cases})


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
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        location = request.POST.get('location')
        if full_name:
            request.user.first_name = full_name
            request.user.save()
        profile.phone = phone
        profile.location = location
        profile.save()
        return redirect('profile_view')
    return render(request, 'accounts/profile.html', {'profile': profile})

