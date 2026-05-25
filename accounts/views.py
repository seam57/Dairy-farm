import json
import os
import base64
from dotenv import load_dotenv
from PIL import Image
from groq import Groq
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from decimal import Decimal

# আপনার মডেলগুলো ইমপোর্ট করা হচ্ছে
from .models import UserProfile, Animal, AnimalGroup, DailyFarmDiary, HealthConsultation, VaccinationRecord

# --- RAG System ---
import json as _json

def _search_rag(query: str, animal_filter: str = None, n: int = 3) -> list:
    """Veterinary knowledge base থেকে relevant তথ্য খোঁজে"""
    RAG_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vet_rag_db.json')
    if not os.path.exists(RAG_DB_PATH):
        return []
    with open(RAG_DB_PATH, 'r', encoding='utf-8') as f:
        db = _json.load(f)
    query_lower = query.lower()
    query_words = set(query_lower.split())
    scored = []
    for doc in db:
        score = 0
        text = doc.get('full_text', '')
        animal_map = {'cow':'গরু','goat':'ছাগল','hen':'মুরগি','duck':'হাঁস'}
        if animal_filter:
            bn = animal_map.get(animal_filter, animal_filter)
            if bn in text or animal_filter in text:
                score += 5
        for word in query_words:
            if len(word) > 1 and word in text:
                score += 2
        if query_lower in text:
            score += 10
        for kw in ['জ্বর','কাশি','ডায়রিয়া','দুধ','ফোলা','ঘা','রক্ত','দুর্বল','খাচ্ছে','ভ্যাকসিন','fever','cough','milk','weak','blood','লালা','পায়ে','মৃত্যু']:
            if kw in query_lower and kw in text:
                score += 3
        if score > 0:
            scored.append((score, doc))
    scored.sort(key=lambda x: -x[0])
    return [doc for _, doc in scored[:n]]

def _build_rag_context(results: list) -> str:
    """RAG results থেকে AI-এর জন্য context তৈরি করে"""
    if not results:
        return ""
    context = "\n\n═══ প্রাসঙ্গিক ভেটেরিনারি জ্ঞানভাণ্ডার (RAG) ═══\n"
    for i, doc in enumerate(results, 1):
        context += f"""
[তথ্য {i}] {doc['title']}
পশু: {doc['animal']} | জরুরিত্ব: {doc['urgency']}
লক্ষণ: {doc['symptoms']}
চিকিৎসা: {doc['treatment']}
প্রতিরোধ: {doc['prevention']}
ভ্যাকসিন: {doc['vaccine']}
"""
    context += "═══════════════════════════════════════════\n"
    return context

# --- Groq AI Configuration ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
groq_client = Groq(api_key=GROQ_API_KEY)

def groq_chat(prompt, image_path=None):
    """Groq দিয়ে AI response নেওয়ার helper function"""
    if image_path:
        # Image সহ — vision model use করো
        with open(image_path, 'rb') as f:
            img_data = base64.b64encode(f.read()).decode('utf-8')
        # image extension detect
        ext = image_path.split('.')[-1].lower()
        mime = 'image/jpeg' if ext in ['jpg','jpeg'] else f'image/{ext}'
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{img_data}"}}
            ]
        }]
        response = groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=messages,
            max_tokens=1500
        )
    else:
        messages = [{"role": "user", "content": prompt}]
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=1500
        )
    return response.choices[0].message.content


# --- Disease Outbreak Alert (Groq Web Search) ---
import threading
_outbreak_cache = {"data": None, "timestamp": None}

def get_outbreak_alert():
    """বাংলাদেশে current disease situation — প্রতি ৬ ঘণ্টায় update"""
    from datetime import datetime, timedelta
    import json as _json

    now = datetime.now()
    if (_outbreak_cache["data"] is not None and
        _outbreak_cache["timestamp"] and
        now - _outbreak_cache["timestamp"] < timedelta(hours=6)):
        return _outbreak_cache["data"]

    try:
        prompt = """তুমি একজন livestock disease surveillance expert।
আজকের তারিখ: """ + now.strftime("%B %Y") + """

বাংলাদেশ ও দক্ষিণ এশিয়ায় এখন কোন কোন পশু-পাখির রোগের প্রকোপ আছে সেটা web থেকে খুঁজে বের করো।
Bird Flu, Newcastle Disease, FMD, Lumpy Skin Disease, PPR, Anthrax সহ যেকোনো রোগ।

নিচের JSON format এ উত্তর দাও, শুধু JSON, আর কিছু না:
{
  "updated": "মাস বছর",
  "alerts": [
    {
      "level": "high/medium/low",
      "disease": "রোগের নাম বাংলায়",
      "disease_en": "English name",
      "affects": "গরু/মুরগি/ছাগল/সব পশু",
      "location": "কোথায় — জেলা বা দেশ",
      "message": "সতর্কবার্তা ২০ শব্দে বাংলায়",
      "action": "করণীয় ১৫ শব্দে বাংলায়",
      "source": "তথ্যসূত্র"
    }
  ]
}

কোনো outbreak না থাকলে: {"updated": "মাস বছর", "alerts": []}"""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            tools=[{"type": "web_search_20250305", "name": "web_search"}]
        )

        # content blocks থেকে text বের করো
        full_text = ""
        if hasattr(response.choices[0].message, 'content') and response.choices[0].message.content:
            full_text = response.choices[0].message.content
        else:
            # tool_use response হলে content list থেকে নাও
            for block in (response.choices[0].message.content or []):
                if hasattr(block, 'text'):
                    full_text += block.text

        full_text = full_text.strip()
        if "```" in full_text:
            full_text = full_text.split("```")[1].replace("json","").strip()

        result = _json.loads(full_text)
        _outbreak_cache["data"] = result
        _outbreak_cache["timestamp"] = now
        return result

    except Exception as e:
        print(f"[OUTBREAK ERROR]: {e}")
        _outbreak_cache["data"] = {"updated": "", "alerts": []}
        _outbreak_cache["timestamp"] = now
        return {"updated": "", "alerts": []}

# --- Farmer Dashboard ---
@login_required
def farmer_dashboard(request):
    error_message = None

    if request.method == "POST" and 'add_animal' in request.POST:
        tag = request.POST.get('tag_id', '').strip()
        cat = request.POST.get('category')
        brd = request.POST.get('breed', '').strip()
        if tag and cat:
            if Animal.objects.filter(tag_id=tag).exists():
                error_message = f'❌ ট্যাগ আইডি "{tag}" আগে থেকেই আছে। অন্য একটি আইডি দিন।'
            else:
                Animal.objects.create(owner=request.user, tag_id=tag, category=cat, breed=brd)
                return redirect('farmer_dashboard')

    animals = Animal.objects.filter(owner=request.user)
    search_query = request.GET.get('search_id', '').strip()

    vaccination_history_list = []
    if search_query:
        vaccination_history_list = VaccinationRecord.objects.filter(
            animal__owner=request.user,
            animal__tag_id__iexact=search_query
        ).order_by('-date')

    vaccinated_count   = animals.filter(last_vaccination_date__isnull=False).count()
    unvaccinated_count = animals.filter(last_vaccination_date__isnull=True).count()
    total_diary_records = DailyFarmDiary.objects.filter(farmer=request.user).count()


    # Disease outbreak alert
    outbreak_alert = get_outbreak_alert()

    return render(request, 'dashboards/farmer.html', {
        'animals': animals,
        'outbreak_alert': outbreak_alert,
        'vaccination_history_list': vaccination_history_list,
        'search_query': search_query,
        'vaccinated_count': vaccinated_count,
        'unvaccinated_count': unvaccinated_count,
        'total_diary_records': total_diary_records,
        'error_message': error_message,
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
            animal_info = f"Type: {target_animal.category}, Breed: {target_animal.breed}" if target_animal else ""
            prompt = f"Livestock Expert. Bangla. {animal_info} User Question: {user_query}"
            response_text = groq_chat(prompt)
        except Exception as e:
            response_text = "AI সার্ভিস এখন ব্যস্ত।"
    return render(request, 'dashboards/diet_planner.html', {'response': response_text})




# --- Delete Animal (সব data সহ মুছে ফেলা) ---
@login_required
def delete_animal_view(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
    if request.method == "POST":
        DailyFarmDiary.objects.filter(animal=animal).delete()
        VaccinationRecord.objects.filter(animal=animal).delete()
        animal.delete()
    return redirect('farmer_dashboard')

# --- AgroTrack/Diary ---
@login_required
def daily_diary_view(request):
    if request.method == "POST":
        if 'clear_agrotrack' in request.POST:
            DailyFarmDiary.objects.filter(farmer=request.user).delete()
            return redirect('daily_diary')
        else:
            animal_id = request.POST.get('animal_id') or ''
            group_id = request.POST.get('group_id') or ''
            animal_obj = None
            group_obj = None
            if animal_id:
                animal_obj = Animal.objects.filter(id=animal_id, owner=request.user).first()
            elif group_id:
                group_obj = AnimalGroup.objects.filter(id=group_id, owner=request.user).first()
            DailyFarmDiary.objects.create(
                farmer=request.user, animal=animal_obj, group=group_obj,
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
    groups = AnimalGroup.objects.filter(owner=request.user)

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

    # ── Group-based ROI — গ্রুপ ভিত্তিক লাভ-ক্ষতি ──
    category_bn = {'cow': 'গরু', 'goat': 'ছাগল', 'hen': 'মুরগি', 'duck': 'হাঁস'}
    group_stats = []
    for g in groups:
        records = history.filter(group=g)
        agg_g = records.aggregate(
            mi=Sum('milk_income'), mt=Sum('meat_income'), ei=Sum('egg_income'),
            fc=Sum('feed_cost'),   mc=Sum('medicine_cost'), oc=Sum('other_cost')
        )
        income  = float((agg_g['mi'] or 0) + (agg_g['mt'] or 0) + (agg_g['ei'] or 0))
        expense = float((agg_g['fc'] or 0) + (agg_g['mc'] or 0) + (agg_g['oc'] or 0))
        group_stats.append({
            'category':     category_bn.get(g.category, g.category),
            'animal_count': g.animal_count,
            'income':       income,
            'expense':      expense,
            'profit':       income - expense,
        })

    # ── One-off per-animal entries — একক পশু এন্ট্রি ──
    oneoff_stats = []
    for animal in animals:
        records = history.filter(animal=animal)
        if records.exists():
            agg_a = records.aggregate(
                mi=Sum('milk_income'), mt=Sum('meat_income'), ei=Sum('egg_income'),
                fc=Sum('feed_cost'),   mc=Sum('medicine_cost'), oc=Sum('other_cost')
            )
            income  = float((agg_a['mi'] or 0) + (agg_a['mt'] or 0) + (agg_a['ei'] or 0))
            expense = float((agg_a['fc'] or 0) + (agg_a['mc'] or 0) + (agg_a['oc'] or 0))
            oneoff_stats.append({
                'tag_id':   animal.tag_id,
                'category': category_bn.get(animal.category, animal.category),
                'income':   income,
                'expense':  expense,
                'profit':   income - expense,
            })

    return render(request, 'dashboards/diary.html', {
        'history':        history,
        'animals':        animals,
        'groups':         groups,
        'chart_dates':    json.dumps(chart_dates),
        'chart_incomes':  json.dumps(chart_incomes),
        'chart_expenses': json.dumps(chart_expenses),
        'pie_data':       json.dumps(pie_data),
        'group_stats':    group_stats,
        'oneoff_stats':   oneoff_stats,
        'total_income':   total_income,
        'total_expense':  total_expense,
        'net_profit':     net_profit,
    })


# --- AI Doctor ---
@login_required
def farm_ai_doctor(request):
    response_text = ""
    user_query    = ""
    image_sent    = False

    if request.method == "POST":
        if 'clear_ai' in request.POST:
            return redirect('farm_ai_doctor')

        user_query = request.POST.get('user_query', '').strip()
        user_image = request.FILES.get('user_image')
        image_sent = user_image is not None

        SYSTEM_PROMPT = (
            "তুমি একজন অভিজ্ঞ ভেটেরিনারি ডাক্তার (Livestock & Poultry Specialist)। "
            "বাংলাদেশের কৃষকদের পশু-পাখির স্বাস্থ্য সমস্যায় সাহায্য করো।\n\n"
            "ভাষার নিয়ম:\n"
            "- ব্যবহারকারী বাংলায় লিখলে বাংলায় উত্তর দাও\n"
            "- English এ লিখলে English এ উত্তর দাও\n"
            "- Banglish (Roman হরফে বাংলা) লিখলে বাংলায় উত্তর দাও\n"
            "- মিশ্র ভাষায় লিখলে বাংলায় উত্তর দাও\n\n"
            "উত্তরের ধাপ:\n"
            "১. সম্ভাব্য রোগ চিহ্নিত করো\n"
            "২. লক্ষণ সহজ ভাষায় ব্যাখ্যা করো\n"
            "৩. প্রাথমিক চিকিৎসা ও করণীয় বলো\n"
            "৪. প্রয়োজনীয় ওষুধ বা ভ্যাকসিনের নাম দাও\n"
            "৫. কখন ডাক্তার দেখাতে হবে জানাও\n\n"
            "উত্তর সংক্ষিপ্ত ও কার্যকর রাখো। "
            "ছবি থাকলে visible লক্ষণ দেখে diagnosis করো।"
        )

        try:
            # RAG — knowledge base থেকে relevant তথ্য খোঁজা
            rag_results = _search_rag(user_query, n=3)
            rag_context = _build_rag_context(rag_results)

            full_prompt = SYSTEM_PROMPT + rag_context + "\n\nকৃষকের প্রশ্ন: " + user_query
            if user_image:
                import tempfile
                suffix = '.' + user_image.name.split('.')[-1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    for chunk in user_image.chunks():
                        tmp.write(chunk)
                    tmp_path = tmp.name
                response_text = groq_chat(full_prompt + "\n[ছবি দেখে diagnosis করো]", image_path=tmp_path)
                os.unlink(tmp_path)
            else:
                response_text = groq_chat(full_prompt)
        except Exception as e:
            error_msg = str(e)
            print(f"[AI DOCTOR ERROR]: {error_msg}")  # terminal এ দেখাবে
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower() or "credential" in error_msg.lower():
                response_text = "❌ GROQ_API_KEY সমস্যা। .env ফাইলে সঠিক GROQ_API_KEY আছে কিনা চেক করুন।"
            elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
                response_text = "⚠️ API quota শেষ। কিছুক্ষণ পর আবার চেষ্টা করুন।"
            elif "network" in error_msg.lower() or "connection" in error_msg.lower():
                response_text = "⚠️ Internet সংযোগ সমস্যা। নেটওয়ার্ক চেক করুন।"
            else:
                response_text = f"❌ AI সার্ভিস Error: {error_msg[:200]}"

    return render(request, 'dashboards/farm_ai.html', {
        'response':   response_text,
        'user_query': user_query,
        'image_sent': image_sent,
    })



# --- AI Debug View (development only) ---
@login_required
def ai_debug_view(request):
    """শুধু development এ use করুন — API key check করতে"""
    from django.http import HttpResponse
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(BASE_DIR, '.env')
    key = os.environ.get('GROQ_API_KEY', 'NOT FOUND')
    env_exists = os.path.exists(env_path)
    msg = f"""
    ENV file exists: {env_exists}
    ENV path: {env_path}
    GROQ_API_KEY found: {'YES - ' + key[:10] + '...' if key != 'NOT FOUND' else 'NO'}
    """
    return HttpResponse(f"<pre>{msg}</pre>")



# --- ML Financial Prediction ---
@login_required
def ml_prediction_view(request):
    import joblib, numpy as np
    from datetime import date

    # Model files path
    MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))

    # Auto-fill values from user's existing data
    from django.db.models import Sum, Avg
    animals       = Animal.objects.filter(owner=request.user)
    animals_count = animals.count()
    history       = DailyFarmDiary.objects.filter(farmer=request.user).order_by('-date')
    current_month = date.today().month

    # আগের মাসের লাভ auto-calculate
    prev_totals  = history.aggregate(
        ti=Sum('milk_income'), tm=Sum('meat_income'), te=Sum('egg_income'),
        tf=Sum('feed_cost'),   tmed=Sum('medicine_cost'), to=Sum('other_cost')
    )
    prev_income  = float((prev_totals['ti'] or 0)+(prev_totals['tm'] or 0)+(prev_totals['te'] or 0))
    prev_expense = float((prev_totals['tf'] or 0)+(prev_totals['tmed'] or 0)+(prev_totals['to'] or 0))
    prev_profit  = round(prev_income - prev_expense, 2)

    prediction = None
    form_data  = {}

    if request.method == 'POST':
        # Form data collect
        form_data = {
            'month':         int(request.POST.get('month', current_month)),
            'num_animals':   int(request.POST.get('num_animals', animals_count)),
            'milk_income':   float(request.POST.get('milk_income', 0) or 0),
            'meat_income':   float(request.POST.get('meat_income', 0) or 0),
            'egg_income':    float(request.POST.get('egg_income',  0) or 0),
            'feed_cost':     float(request.POST.get('feed_cost',   0) or 0),
            'medicine_cost': float(request.POST.get('medicine_cost', 0) or 0),
            'other_cost':    float(request.POST.get('other_cost',  0) or 0),
            'prev_profit':   float(request.POST.get('prev_profit', prev_profit) or 0),
        }

        try:
            # Load models
            profit_model  = joblib.load(os.path.join(MODEL_DIR, 'profit_model.pkl'))
            profit_scaler = joblib.load(os.path.join(MODEL_DIR, 'profit_scaler.pkl'))
            trend_model   = joblib.load(os.path.join(MODEL_DIR, 'trend_model.pkl'))
            trend_scaler  = joblib.load(os.path.join(MODEL_DIR, 'trend_scaler.pkl'))

            import pandas as pd
            features = ['month','num_animals','milk_income','meat_income',
                        'egg_income','feed_cost','medicine_cost','other_cost','prev_profit']
            X = pd.DataFrame([[form_data[f] for f in features]], columns=features)

            # Predict profit
            X_scaled_p     = profit_scaler.transform(X)
            predicted_profit = float(profit_model.predict(X_scaled_p)[0])

            # Predict trend
            X_scaled_t  = trend_scaler.transform(X)
            trend        = int(trend_model.predict(X_scaled_t)[0])
            confidence   = round(max(trend_model.predict_proba(X_scaled_t)[0]) * 100, 1)

            # Profit change vs prev
            diff = predicted_profit - form_data['prev_profit']
            if diff > 0:
                profit_change = f"+৳{diff:,.0f} বেশি"
            else:
                profit_change = f"৳{abs(diff):,.0f} কম"

            # Feature importance
            importances = profit_model.feature_importances_
            imp_total   = sum(importances)
            imp_labels  = ['মাস','পশু সংখ্যা','দুধ আয়','মাংস আয়',
                           'ডিম আয়','খাবার খরচ','ওষুধ খরচ','অন্যান্য','গত মাসের লাভ']
            importance_list = sorted(
                [{'name': imp_labels[i], 'pct': round(v/imp_total*100, 1)}
                 for i, v in enumerate(importances)],
                key=lambda x: -x['pct']
            )[:6]

            # Smart advice
            advice_list = []
            total_income  = form_data['milk_income']+form_data['meat_income']+form_data['egg_income']
            total_expense = form_data['feed_cost']+form_data['medicine_cost']+form_data['other_cost']

            if predicted_profit > 0 and trend == 1:
                advice_list.append({
                    'icon':'fa-seedling','bg':'#d1fae5','color':'#059669',
                    'title':'বিনিয়োগ বাড়ানোর সুযোগ',
                    'text':f'আগামী মাস লাভজনক দেখাচ্ছে। নতুন পশু কেনার কথা ভাবতে পারেন।'
                })
            if form_data['feed_cost'] > total_income * 0.5:
                advice_list.append({
                    'icon':'fa-wheat-awn','bg':'#fef3c7','color':'#d97706',
                    'title':'খাবার খরচ বেশি',
                    'text':f'আয়ের {round(form_data["feed_cost"]/max(total_income,1)*100)}% খাবারে যাচ্ছে। স্থানীয় বিকল্প খোঁজুন।'
                })
            if form_data['milk_income'] < form_data['num_animals'] * 500:
                advice_list.append({
                    'icon':'fa-cow','bg':'#dbeafe','color':'#2563eb',
                    'title':'দুধের উৎপাদন বাড়ানো যায়',
                    'text':'প্রতি পশু থেকে দুধের আয় কম। পুষ্টিকর খাবার ও নিয়মিত ভ্যাকসিন দিন।'
                })
            if predicted_profit < 0:
                advice_list.append({
                    'icon':'fa-triangle-exclamation','bg':'#fee2e2','color':'#ef4444',
                    'title':'লোকসানের ঝুঁকি আছে',
                    'text':'অপ্রয়োজনীয় খরচ কমান এবং আয়ের নতুন উৎস খুঁজুন।'
                })
            if not advice_list:
                advice_list.append({
                    'icon':'fa-check-circle','bg':'#d1fae5','color':'#059669',
                    'title':'খামার সুষম অবস্থায় আছে',
                    'text':'বর্তমান ব্যবস্থাপনা চালিয়ে যান।'
                })

            prediction = {
                'profit':           predicted_profit,
                'profit_formatted': f'{predicted_profit:,.0f}',
                'profit_change':    profit_change,
                'trend':            trend,
                'confidence':       confidence,
                'advice':           advice_list,
                'importance':       importance_list,
            }

        except FileNotFoundError:
            prediction = {'error': 'Model file পাওয়া যায়নি। train_model.py run করুন।'}
        except Exception as e:
            prediction = {'error': f'Prediction error: {str(e)}'}

    return render(request, 'dashboards/prediction.html', {
        'prediction':    prediction,
        'form_data':     form_data,
        'animals_count': animals_count,
        'current_month': current_month,
        'prev_profit':   prev_profit,
    })




# --- AI Financial Prediction (Groq দিয়ে) ---
@login_required
def ai_prediction_view(request):
    from django.db.models import Sum

    animals = Animal.objects.filter(owner=request.user)
    animals_count = animals.count()
    history = DailyFarmDiary.objects.filter(farmer=request.user).order_by('-date')
    total_records = history.count()

    all_totals = history.aggregate(
        ti=Sum('milk_income'), tm=Sum('meat_income'), te=Sum('egg_income'),
        tf=Sum('feed_cost'), tmed=Sum('medicine_cost'), to=Sum('other_cost')
    )
    total_income  = float((all_totals['ti'] or 0)+(all_totals['tm'] or 0)+(all_totals['te'] or 0))
    total_expense = float((all_totals['tf'] or 0)+(all_totals['tmed'] or 0)+(all_totals['to'] or 0))
    net_profit    = total_income - total_expense

    recent_rows = []
    for r in list(history[:7]):
        recent_rows.append(
            f"  {r.date}: আয়=৳{float(r.total_income):,.0f}, ব্যয়=৳{float(r.total_expense):,.0f}, লাভ=৳{float(r.net_profit):,.0f}"
        )

    group_roi_rows = []
    category_bn = {'cow': 'গরু', 'goat': 'ছাগল', 'hen': 'মুরগি', 'duck': 'হাঁস'}
    for grp in AnimalGroup.objects.filter(owner=request.user):
        recs = history.filter(group=grp)
        if recs.exists():
            agg = recs.aggregate(
                mi=Sum('milk_income'), mt=Sum('meat_income'), ei=Sum('egg_income'),
                fc=Sum('feed_cost'), mc=Sum('medicine_cost'), oc=Sum('other_cost')
            )
            inc = float((agg['mi'] or 0)+(agg['mt'] or 0)+(agg['ei'] or 0))
            exp = float((agg['fc'] or 0)+(agg['mc'] or 0)+(agg['oc'] or 0))
            group_roi_rows.append(
                f"  {category_bn.get(grp.category, grp.category)} গ্রুপ ({grp.animal_count}টি পশু): আয়=৳{inc:,.0f} ব্যয়=৳{exp:,.0f} লাভ=৳{inc-exp:,.0f}"
            )

    prediction_raw = None
    error = None
    has_data = total_records > 0

    if request.method == 'POST':
        if not has_data:
            error = "এখনো কোনো diary রেকর্ড নেই। আগে AgroTrack Diary-তে data যোগ করুন।"
        else:
            prompt = f"""তুমি একজন কৃষি অর্থনীতিবিদ।
নিচের বাংলাদেশি ডেইরি ফার্মের real data দেখে আগামী মাসের prediction দাও।

মোট পশু: {animals_count}টি
মোট রেকর্ড: {total_records}টি
সর্বমোট আয়: ৳{total_income:,.0f}
সর্বমোট ব্যয়: ৳{total_expense:,.0f}
সর্বমোট লাভ: ৳{net_profit:,.0f}

সাম্প্রতিক ৭টি রেকর্ড:
{chr(10).join(recent_rows) if recent_rows else "  কোনো রেকর্ড নেই"}

গ্রুপ ভিত্তিক ROI:
{chr(10).join(group_roi_rows) if group_roi_rows else "  কোনো গ্রুপ নেই"}

নিচের format-এ বাংলায় উত্তর দাও:

📊 বর্তমান অবস্থা:
[সংক্ষিপ্ত বিশ্লেষণ]

📈 আগামী মাসের পূর্বাভাস:
আনুমানিক আয়: ৳[সংখ্যা]
আনুমানিক ব্যয়: ৳[সংখ্যা]
আনুমানিক লাভ: ৳[সংখ্যা]
ট্রেন্ড: [বাড়বে/কমবে/স্থিতিশীল]

⚠️ ঝুঁকি:
[২-৩টি bullet point]

✅ পরামর্শ:
[৩-৪টি bullet point]

💡 সেরা সুযোগ:
[১টি focus area]"""
            try:
                prediction_raw = groq_chat(prompt)
            except Exception as e:
                error = f"AI সংযোগ সমস্যা: {str(e)[:200]}"

    return render(request, 'dashboards/prediction.html', {
        'prediction_raw': prediction_raw,
        'error': error,
        'has_data': has_data,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_profit': net_profit,
        'total_records': total_records,
        'animals_count': animals_count,
    })

# --- Animal Analysis (AI + Real Data) ---
@login_required
def animal_analysis_view(request):
    from django.db.models import Q
    animals = Animal.objects.filter(owner=request.user)
    analysis       = None
    selected_animal = None
    user_problem   = ""
    animal_income  = animal_expense = animal_profit = animal_records = 0
    group_income   = group_expense  = group_profit  = 0

    if request.method == "POST":
        animal_id    = request.POST.get("animal_id", "").strip()
        user_problem = request.POST.get("user_problem", "").strip()

        if animal_id:
            selected_animal = Animal.objects.filter(id=animal_id, owner=request.user).first()

        if selected_animal and user_problem:
            from django.db.models import Sum
            # ── Per-animal one-off entries ──
            diary_records = DailyFarmDiary.objects.filter(
                farmer=request.user, animal=selected_animal
            ).order_by("-date")

            vax_records = VaccinationRecord.objects.filter(
                animal=selected_animal
            ).order_by("-date")

            agg = diary_records.aggregate(
                mi=Sum("milk_income"), mt=Sum("meat_income"), ei=Sum("egg_income"),
                fc=Sum("feed_cost"),   mc=Sum("medicine_cost"), oc=Sum("other_cost")
            )
            animal_income  = float((agg["mi"] or 0)+(agg["mt"] or 0)+(agg["ei"] or 0))
            animal_expense = float((agg["fc"] or 0)+(agg["mc"] or 0)+(agg["oc"] or 0))
            animal_profit  = animal_income - animal_expense
            animal_records = diary_records.count()

            # ── Group context for this animal's category ──
            group_records = DailyFarmDiary.objects.filter(
                farmer=request.user,
                group__owner=request.user,
                group__category=selected_animal.category,
            )
            gagg = group_records.aggregate(
                mi=Sum("milk_income"), mt=Sum("meat_income"), ei=Sum("egg_income"),
                fc=Sum("feed_cost"),   mc=Sum("medicine_cost"), oc=Sum("other_cost")
            )
            group_income  = float((gagg["mi"] or 0)+(gagg["mt"] or 0)+(gagg["ei"] or 0))
            group_expense = float((gagg["fc"] or 0)+(gagg["mc"] or 0)+(gagg["oc"] or 0))
            group_profit  = group_income - group_expense

            recent_records = []
            for r in diary_records[:5]:
                recent_records.append(
                    f"  {r.date}: আয়=৳{float(r.total_income):,.0f}, ব্যয়=৳{float(r.total_expense):,.0f}, লাভ=৳{float(r.net_profit):,.0f}"
                )

            vax_list = [str(v.date) for v in vax_records[:5]]
            vax_info = ", ".join(vax_list) if vax_list else "কোনো রেকর্ড নেই"

            category_bn = {"cow":"গরু","goat":"ছাগল","hen":"মুরগি","duck":"হাঁস"}.get(
                selected_animal.category, selected_animal.category
            )

            rag_results = _search_rag(
                user_problem,
                animal_filter=selected_animal.category,
                n=3
            )
            rag_context = _build_rag_context(rag_results)

            prompt = f"""তুমি একজন অভিজ্ঞ ভেটেরিনারি ডাক্তার এবং কৃষি অর্থনীতিবিদ।
নিচের RAG knowledge base থেকে প্রাসঙ্গিক তথ্য ব্যবহার করো:{rag_context}
নিচে একটি পশুর real database থেকে নেওয়া তথ্য দেওয়া আছে। এই তথ্যের ভিত্তিতে কৃষকের প্রশ্নের উত্তর দাও।

═══ পশুর তথ্য ═══
আইডি       : {selected_animal.tag_id}
ধরন        : {category_bn}
জাত        : {selected_animal.breed or "অজানা"}
শেষ ভ্যাকসিন: {selected_animal.last_vaccination_date or "দেওয়া হয়নি"}

═══ এই পশুর একক রেকর্ড (one-off entries) ═══
মোট আয়     : ৳{animal_income:,.0f}
মোট ব্যয়    : ৳{animal_expense:,.0f}
নিট লাভ     : ৳{animal_profit:,.0f}
মোট রেকর্ড  : {animal_records} টি

═══ {category_bn} গ্রুপের সামগ্রিক হিসাব (এই পশু সেই গ্রুপের অন্তর্ভুক্ত) ═══
মোট আয়     : ৳{group_income:,.0f}
মোট ব্যয়    : ৳{group_expense:,.0f}
নিট লাভ     : ৳{group_profit:,.0f}

═══ সাম্প্রতিক ৫টি রেকর্ড ═══
{chr(10).join(recent_records) if recent_records else "  কোনো রেকর্ড নেই"}

═══ ভ্যাকসিনেশন ইতিহাস ═══
{vax_info}

═══ কৃষকের প্রশ্ন / সমস্যা ═══
{user_problem}

═══ তোমার কাজ ═══
উপরের real data বিশ্লেষণ করে নিচের format এ উত্তর দাও (বাংলায়):

🔍 সমস্যা চিহ্নিতকরণ:
[data দেখে কী সমস্যা বোঝা যাচ্ছে তা বলো]

💊 তাৎক্ষণিক করণীয়:
[এখনই কী করতে হবে, ধাপে ধাপে]

💰 আর্থিক বিশ্লেষণ:
[গ্রুপ ও একক হিসাব দেখে মন্তব্য করো]

📈 পরবর্তী মাসের পূর্বাভাস:
[বর্তমান trend দেখে আগামী মাস কেমন যাবে]

✅ দীর্ঘমেয়াদী পরামর্শ:
[এই পশুর জন্য ২-৩টি গুরুত্বপূর্ণ পরামর্শ]

উত্তর সংক্ষিপ্ত, practical এবং বাংলাদেশের প্রেক্ষাপট অনুযায়ী হওয়া উচিত।"""

            try:
                analysis = groq_chat(prompt)
            except Exception as e:
                analysis = f"AI সার্ভিস এই মুহূর্তে সংযুক্ত হতে পারছে না।\nError: {str(e)}"

    return render(request, "dashboards/animalanalysis.html", {
        "animals":         animals,
        "selected_animal": selected_animal,
        "user_problem":    user_problem,
        "analysis":        analysis,
        "animal_income":   animal_income,
        "animal_expense":  animal_expense,
        "animal_profit":   animal_profit,
        "animal_records":  animal_records,
        "group_income":    group_income,
        "group_expense":   group_expense,
        "group_profit":    group_profit,
    })


# --- Disease News View ---
@login_required
def disease_news_view(request):
    import json as _json
    from datetime import datetime, timedelta

    # Refresh করলে cache clear
    if request.GET.get('refresh'):
        _outbreak_cache["data"] = None
        _outbreak_cache["timestamp"] = None

    outbreak_data = get_outbreak_alert()

    # পুরনো single-alert format হলে convert করো
    if isinstance(outbreak_data, dict) and 'alerts' not in outbreak_data:
        if outbreak_data.get('has_alert'):
            outbreak_data = {
                "updated": datetime.now().strftime("%B %Y"),
                "alerts": [{
                    "level": outbreak_data.get("level", "medium"),
                    "disease": outbreak_data.get("disease", ""),
                    "disease_en": "",
                    "affects": "সব পশু",
                    "location": outbreak_data.get("location", ""),
                    "message": outbreak_data.get("message", ""),
                    "action": outbreak_data.get("action", ""),
                    "source": ""
                }]
            }
        else:
            outbreak_data = {"updated": "", "alerts": []}

    return render(request, 'dashboards/disease_news.html', {
        'outbreak_data': outbreak_data,
    })

# --- Authentication ---
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            profile = UserProfile.objects.filter(user=user).first()
            if profile and profile.role == 'doctor':
                return redirect('doctor_dashboard')
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
        request.user.first_name = request.POST.get('full_name', '').strip()
        request.user.save()
        profile.phone    = request.POST.get('phone', '').strip()
        profile.location = request.POST.get('location', '').strip()
        profile.save()
        return redirect('/profile/?saved=1')
    return render(request, 'accounts/profile.html', {'profile': profile})