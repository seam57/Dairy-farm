from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
# models থেকে UserProfile ইমপোর্ট করা হলো (যাতে আর এরর না আসে)
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
        for field in self.fields.values():
            field.help_text = None  
            
            
            field.widget.attrs.update({
                'class': 'form-control', 
                'placeholder': f'Enter {field.label}'
            })

    class Meta(UserCreationForm.Meta):
        model = User
        # আপনি চাইলে এখানে অতিরিক্ত ফিল্ড যোগ করতে পারেন
        fields = UserCreationForm.Meta.fields