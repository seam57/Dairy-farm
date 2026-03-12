from django.urls import path
from . import views

urlpatterns = [
    # ১. হোম এবং লগইন
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'), # এটি এরর ঠিক করবে
    path('logout/', views.logout_view, name='logout'),

    # ২. ড্যাশবোর্ডগুলো
    path('farmer/', views.farmer_dashboard, name='farmer_dashboard'),
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),

    # ৩. অ্যাকশনগুলো
    path('report-problem/<int:animal_id>/', views.report_problem, name='report_problem'),
    path('milk-record/<int:animal_id>/', views.milk_record, name='milk_record'),
]