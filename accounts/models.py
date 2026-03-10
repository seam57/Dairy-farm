from django.db import models
from django.contrib.auth.models import User

# ১. ইউজার প্রোফাইল: কে Farmer আর কে Doctor তা নির্ধারণ করবে
class Profile(models.Model):
    ROLE_CHOICES = (
        ('farmer', 'Farmer'),
        ('doctor', 'Doctor'),
        ('manager', 'Manager'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='farmer')
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

# ২. পশুর তথ্য: যেখানে ভ্যাক্সিন এবং দুধের মূল রেকর্ড থাকবে
class Animal(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='animals')
    tag_id = models.CharField(max_length=50, unique=True) # যেমন: COW-001
    breed = models.CharField(max_length=100) # জাত
    age = models.IntegerField(help_text="Age in months")
    weight = models.FloatField(help_text="Weight in kg")
    last_vaccination_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.tag_id} - {self.breed}"

# ৩. দুধের হিসাব (Daily Milk Production)
class MilkRecord(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='milk_records')
    date = models.DateField(auto_now_add=True)
    amount_liters = models.FloatField()

    def __str__(self):
        return f"{self.animal.tag_id} - {self.date} - {self.amount_liters}L"

# ৪. ডাক্তার কানেকশন: খামারি সমস্যা জানালে ডাক্তার এখানে দেখবে
class HealthConsultation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('checked', 'Checked'),
    )
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    farmer_note = models.TextField(help_text="পশুর কী সমস্যা হচ্ছে লিখুন") # যেমন: দুধ কম হচ্ছে
    doctor_prescription = models.TextField(blank=True, null=True) # ডাক্তার পরামর্শ দিবে
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.animal.tag_id} - {self.status}"