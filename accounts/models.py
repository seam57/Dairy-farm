from django.db import models
from django.contrib.auth.models import User

# ১. ইউজার প্রোফাইল মডেল
class UserProfile(models.Model):
    ROLE_CHOICES = [('farmer', 'Farmer'), ('doctor', 'Doctor')]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='farmer')

    def __str__(self):
        return f"{self.user.username} - {self.role}"

# ২. পশুপাখির তথ্য রাখার মডেল
class Animal(models.Model):
    # ড্যাশবোর্ডে হাঁস (Duck) অপশন থাকলে এখানেও যোগ করা ভালো
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

# ৩. দৈনিক খামার ডায়েরি (আয়-ব্যয়ের হিসাব)
class DailyFarmDiary(models.Model):
    farmer = models.ForeignKey(User, on_delete=models.CASCADE)
    animal = models.ForeignKey(Animal, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    
    # আয়ের খাতসমূহ
    milk_income = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    meat_income = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    egg_income = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # ব্যয়ের খাতসমূহ
    feed_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    medicine_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    other_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # ড্যাশবোর্ডের গ্রাফের জন্য property (এগুলো পরিবর্তন করবেন না, কারণ views এগুলো ব্যবহার করছে)
    @property
    def total_income(self):
        return float(self.milk_income + self.meat_income + self.egg_income)

    @property
    def total_expense(self):
        return float(self.feed_cost + self.medicine_cost + self.other_cost)

    @property
    def net_profit(self):
        return self.total_income - self.total_expense

# ৪. স্বাস্থ্য পরামর্শ মডেল
class HealthConsultation(models.Model):
    farmer = models.ForeignKey(User, on_delete=models.CASCADE)
    animal_reg_id = models.CharField(max_length=50) # এখানে Animal ForeignKey করলে আরও ভালো হতো
    symptoms = models.TextField()
    status = models.CharField(max_length=20, default='Pending')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Case: {self.animal_reg_id} - {self.status}"