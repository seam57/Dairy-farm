from django.contrib import admin
from .models import UserProfile, Animal, HealthConsultation

admin.site.register(UserProfile)
admin.site.register(Animal)
admin.site.register(HealthConsultation)