from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.farmer_dashboard, name='farmer_dashboard'),
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('diary/', views.daily_diary_view, name='daily_diary'),
    path('farm-ai/', views.farm_ai_doctor, name='farm_ai_doctor'),
    path('update-vaccine/<int:animal_id>/', views.update_vaccine, name='update_vaccine'),
    # প্রোফাইল ভিউ এর জন্য নিচের লাইনটি যোগ করা হলো
    path('profile/', views.profile_view, name='profile_view'), 
]