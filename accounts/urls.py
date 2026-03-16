from django.urls import path
from . import views

urlpatterns = [
    # ১. প্রোফাইল ও অথেনটিকেশন
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile_view'),

    # ২. ড্যাশবোর্ড
    path('farmer/', views.farmer_dashboard, name='farmer_dashboard'),
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),

    # ৩. ভ্যাকসিন আপডেট (এটি আপনার ভিউতে আছে)
    path('update-vaccine/<int:animal_id>/', views.update_vaccine, name='update_vaccine'),

    # ৪. অন্যান্য অ্যাকশন (নিশ্চিত করুন এই নামগুলো views.py এ আছে)
    path('report-problem/<int:animal_id>/', views.report_problem, name='report_problem'),
    path('milk-record/<int:animal_id>/', views.milk_record, name='milk_record'),
    path('prescription/<int:case_id>/', views.add_prescription, name='add_prescription'),
]