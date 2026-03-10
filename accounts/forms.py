from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES, 
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    phone = forms.CharField(
        max_length=15, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'})
    )

    class Meta:
        model = User
        fields = ['username', 'email'] 

    def save(self, commit=True):
        
        user = super().save(commit=False)
        if commit:
            user.save()
            
            Profile.objects.update_or_create(
                user=user,
                defaults={
                    'role': self.cleaned_data.get('role'),
                    'phone': self.cleaned_data.get('phone')
                }
            )
        return user