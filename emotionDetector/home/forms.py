from django import forms
from django.forms import ModelForm
from .models import ModeratorUser
from .models import EmotionData
from .models import Gender
from django.contrib.auth.models import User


class ModeratorUserForm(ModelForm):
    class Meta:
        model = ModeratorUser
        fields = ['name', 'username', 'age', 'gender', 'phone', 'email', 'password', 'address']
        widgets = {
            'gender': forms.Select(attrs={'class': 'myInput'})
        }

    def save(self, *args, **kwargs):
        cleaned_data = self.cleaned_data
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        email = cleaned_data.get('email')
        name = cleaned_data.get('name')

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=name
        )

        instance = super().save(*args, **kwargs)
        return instance


class EmotionDataForm(forms.ModelForm):
    class Meta:
        model = EmotionData
        fields = ['date', 'happy', 'sad', 'surprise', 'angry', 'fear', 'neutral', 'processed_users']