from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
# models থেকে UserProfile ইমপোর্ট করা হলো (যাতে আর এরর না আসে)
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # ১. সব ফিল্ড থেকে হিজিবিজি হেল্প টেক্সট (যেমন: 150 characters...) রিমুভ করা
        for field in self.fields.values():
            field.help_text = None  
            
            # ২. সব ইনপুট বক্সে বুটস্ট্র্যাপ ক্লাস যোগ করা যাতে দেখতে সুন্দর হয়
            field.widget.attrs.update({
                'class': 'form-control', 
                'placeholder': f'Enter {field.label}'
            })

    class Meta(UserCreationForm.Meta):
        model = User
        # আপনি চাইলে এখানে অতিরিক্ত ফিল্ড যোগ করতে পারেন
        fields = UserCreationForm.Meta.fields