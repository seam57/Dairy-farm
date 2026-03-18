from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=[('farmer', 'Farmer'), ('doctor', 'Doctor')])

    def __str__(self):
        return f"{self.user.username} - {self.role}"

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
    last_vaccination = models.DateField(null=True, blank=True) 

    def __str__(self):
        return f"{self.tag_id} ({self.category})"

class Production(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    milk_amount = models.FloatField(default=0.0) 
    egg_count = models.IntegerField(default=0)

class Vaccination(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    vaccine_name = models.CharField(max_length=100)
    last_date = models.DateField()
    next_due_date = models.DateField() 
    is_done = models.BooleanField(default=False)

class HealthConsultation(models.Model):
    farmer = models.ForeignKey(User, on_delete=models.CASCADE)
    animal_reg_id = models.CharField(max_length=50)
    symptoms = models.TextField()
    report_image = models.ImageField(upload_to='health_reports/', null=True, blank=True)
    status = models.CharField(max_length=20, default='Pending')
    doctor_advice = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SWIT Report: {self.animal_reg_id} - {self.status}"

class DailyFarmDiary(models.Model):
    farmer = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    animal_sold_count = models.IntegerField(default=0)
    animal_sold_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    milk_liters = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    milk_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    egg_count = models.IntegerField(default=0)
    egg_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    meat_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    meat_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    feed_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def total_daily_income(self):
        return self.animal_sold_price + self.milk_price + self.egg_price + self.meat_price

    def __str__(self):
        return f"Diary - {self.date} - {self.farmer.username}"