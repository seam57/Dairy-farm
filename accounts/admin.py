from django.contrib import admin
from .models import Profile, Animal, HealthConsultation

admin.site.register(Profile)
admin.site.register(Animal)
admin.site.register(HealthConsultation)