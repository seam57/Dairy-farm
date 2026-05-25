# Livestock Pro — Dairy Farm Management

A Django-based livestock and dairy farm management system with AI-powered features: disease diagnosis (with image upload), bilingual (Bengali/English) veterinary chat, financial tracking, and outbreak alerts. Built around the Groq API and a small RAG knowledge base of common cattle/poultry diseases.

## Tech Stack

- **Backend**: Django (Python 3.11)
- **Database**: SQLite (local) / PostgreSQL (production via `dj-database-url`)
- **AI**: Groq API (`llama-3.3-70b-versatile` for text, `llama-4-scout-17b` for vision)
- **Frontend**: Django templates + Bootstrap 5 + Chart.js
- **Deployment**: Render.com (Gunicorn + WhiteNoise)

## Features

- Farmer and Doctor dashboards (role-based)
- Animal registry (cows, goats, hens, ducks) with vaccination tracking
- **AgroTrack** — daily income/expense diary with per-animal ROI
- **AI Doctor** — chat-based disease diagnosis with image upload
- **AI Financial Forecast** — next-month profit prediction
- Real-time disease outbreak alerts (cached 6h)

---

## Run Locally

### 1. Prerequisites

- Python 3.11+
- `pip` and `venv`
- A [Groq API key](https://console.groq.com/keys) (free tier works)

### 2. Clone & enter the project

```bash
git clone <your-repo-url>
cd Dairy-farm
```

### 3. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate    # Linux / macOS
# venv\Scripts\activate     # Windows
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Create a `.env` file

In the project root, create `.env` with:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
GROQ_API_KEY=your-groq-api-key-here
```

Generate a Django secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 6. Run database migrations

```bash
python manage.py migrate
```

### 7. Create a superuser (optional, for `/admin/`)

```bash
python manage.py createsuperuser
```

### 8. Start the development server

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

---

## Project Structure

```
Dairy-farm/
├── accounts/               # Main app: models, views, AI logic, RAG
│   ├── models.py           # UserProfile, Animal, DailyFarmDiary, etc.
│   ├── views.py            # Dashboards + AI endpoints
│   ├── vet_knowledge.py    # Source veterinary knowledge
│   ├── setup_rag.py        # Builds vet_rag_db.json
│   └── vet_rag_db.json     # RAG knowledge base
├── livestock_project/      # Django settings & root URLs
├── templates/              # Dashboards, auth, AI chat UI
├── media/                  # User-uploaded images
├── staticfiles/            # Collected static files
├── manage.py
├── requirements.txt
└── render.yaml             # Render.com deploy config
```

## Key Routes

| Route | Description |
|---|---|
| `/` | Login |
| `/register/` | Sign up (creates farmer profile) |
| `/dashboard/` | Farmer dashboard |
| `/doctor/` | Doctor dashboard |
| `/diary/` | Daily income/expense tracker |
| `/farm-ai/` | AI Doctor chat (with image upload) |
| `/animal-analysis/` | Per-animal AI + DB analysis |
| `/ai-prediction/` | Financial forecast |
| `/disease-news/` | Live outbreak alerts |
| `/admin/` | Django admin |

---

## Troubleshooting

- **`GROQ_API_KEY` missing** — AI features will fail. Set it in `.env`.
- **`psycopg2` install error on local** — safe to ignore; SQLite is used locally. To skip it, install deps individually without `psycopg2-binary`.
- **Static files not loading** — run `python manage.py collectstatic` once.
- **Port already in use** — `python manage.py runserver 8001`.
