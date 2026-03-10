from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from accounts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    
    path('', views.home, name='home'),

    
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    
   
    path('farmer/', views.farmer_dashboard, name='farmer_dashboard'),
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    
    
    path('report/<int:animal_id>/', views.report_problem, name='report_problem'),
]