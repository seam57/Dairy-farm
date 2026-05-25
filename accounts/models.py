from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [('farmer', 'Farmer'), ('doctor', 'Doctor')]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='farmer')
    phone = models.CharField(max_length=15, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Animal(models.Model):
    CATEGORY_CHOICES = [
        ('cow', 'Cow'),
        ('goat', 'Goat'),
        ('hen', 'Hen'),
        ('duck', 'Duck')
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    tag_id = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    breed = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    last_vaccination_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.tag_id} - {self.category}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        AnimalGroup.objects.get_or_create(owner=self.owner, category=self.category)

class AnimalGroup(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='animal_groups')
    category = models.CharField(max_length=10, choices=Animal.CATEGORY_CHOICES)

    class Meta:
        unique_together = ('owner', 'category')

    def __str__(self):
        return f"{self.owner.username} - {self.get_category_display()} group"

    @property
    def animal_count(self):
        return Animal.objects.filter(owner=self.owner, category=self.category, is_active=True).count()

class DailyFarmDiary(models.Model):
    farmer = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(AnimalGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='diary_entries')
    animal = models.ForeignKey(Animal, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(auto_now_add=True)

    milk_income = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    meat_income = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    egg_income = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    feed_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    medicine_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    other_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~(Q(group__isnull=False) & Q(animal__isnull=False)),
                name='diary_group_xor_animal',
            ),
        ]

    @property
    def total_income(self):
        return float(self.milk_income + self.meat_income + self.egg_income)

    @property
    def total_expense(self):
        return float(self.feed_cost + self.medicine_cost + self.other_cost)

    @property
    def net_profit(self):
        return self.total_income - self.total_expense

class HealthConsultation(models.Model):
    farmer = models.ForeignKey(User, on_delete=models.CASCADE)
    animal_reg_id = models.CharField(max_length=50)
    symptoms = models.TextField()
    status = models.CharField(max_length=20, default='Pending')
    date = models.DateTimeField(auto_now_add=True)

class VaccinationRecord(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='vaccinations')
    date = models.DateField()

    def __str__(self):
        return f"{self.animal.tag_id} - {self.date}"
