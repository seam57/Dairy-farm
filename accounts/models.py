from django.db import models
from django.contrib.auth.models import User

# ১. ইউজার প্রোফাইল (ফার্মার না ডাক্তার তা নির্ধারণের জন্য)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=[('farmer', 'Farmer'), ('doctor', 'Doctor')])

    def __str__(self):
        return f"{self.user.username} - {self.role}"

# ২. পশুর মডেল (আপনার নকশা অনুযায়ী ক্যাটাগরি আপডেট করা হয়েছে)
class Animal(models.Model):
    CATEGORY_CHOICES = [
        ('cow', 'Cow'),
        ('goat', 'Goat'),
        ('hen', 'Hen'),
        ('duck', 'Duck'),
        ('bird', 'Bird'),
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    tag_id = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    breed = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    # আপনার নকশা অনুযায়ী সরাসরি ভ্যাকসিন তারিখ রাখার জন্য নতুন ফিল্ড
    last_vaccination = models.DateField(null=True, blank=True) 

    def __str__(self):
        return f"{self.tag_id} ({self.category})"

# ৩. উৎপাদন রেকর্ড (দুধ বা ডিম)
class Production(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    milk_amount = models.FloatField(default=0.0) 
    egg_count = models.IntegerField(default=0)

# ৪. ডাক্তার এবং ভ্যাকসিনের বিস্তারিত রেকর্ড
class Vaccination(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    vaccine_name = models.CharField(max_length=100)
    last_date = models.DateField()
    next_due_date = models.DateField() 
    is_done = models.BooleanField(default=False)

# ৫. ডাক্তার কনসালটেশন (ফার্মার রিপোর্ট করলে এখানে আসবে)
class HealthConsultation(models.Model):
    farmer = models.ForeignKey(User, on_delete=models.CASCADE)
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    symptoms = models.TextField()
    status = models.CharField(max_length=20, default='Pending') # Pending, Solved
    doctor_advice = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Case: {self.animal.tag_id} - {self.status}"