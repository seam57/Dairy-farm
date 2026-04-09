from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'), # নাম 'logout' রাখা হয়েছে
    path('profile/', views.profile_view, name='profile_view'),
    path('farmer/', views.farmer_dashboard, name='farmer_dashboard'),
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('diary/', views.daily_diary_view, name='daily_diary'),
    path('report-problem/<int:animal_id>/', views.report_problem, name='report_problem'),
    path('update-vaccine/<int:animal_id>/', views.update_vaccine, name='update_vaccine'),
    path('swit-report/', views.swit_report, name='swit_report'),
    path('milk-record/<int:animal_id>/', views.milk_record, name='milk_record'),
    path('add-prescription/<int:case_id>/', views.add_prescription, name='add_prescription'),
]