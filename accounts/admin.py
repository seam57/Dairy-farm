from django.contrib import admin
from .models import UserProfile, Animal, AnimalGroup, DailyFarmDiary, HealthConsultation

admin.site.register(UserProfile)
admin.site.register(Animal)
admin.site.register(AnimalGroup)
admin.site.register(DailyFarmDiary)
admin.site.register(HealthConsultation)