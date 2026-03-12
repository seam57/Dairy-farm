from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = (('farmer', 'Farmer'), ('doctor', 'Doctor'))
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='farmer')

class Animal(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    tag_id = models.CharField(max_length=50)
    breed = models.CharField(max_length=100)
    age = models.IntegerField()
    weight = models.FloatField()

    def __str__(self):
        return self.tag_id

class MilkProduction(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='milk_records')
    date = models.DateField(auto_now_add=True)
    amount = models.FloatField()

class HealthConsultation(models.Model):
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultations')
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    symptoms = models.TextField()
    doctor_advice = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, default='Pending')
    date = models.DateTimeField(auto_now_add=True)