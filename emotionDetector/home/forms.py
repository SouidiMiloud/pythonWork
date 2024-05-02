from django import forms
from django.forms import ModelForm
from .models import ModeratorUser
from .models import EmotionData
from .models import Gender
from .models import Role
from django.contrib.auth.models import User


class ModeratorUserForm(ModelForm):
    class Meta:
        model = ModeratorUser
        fields = ['name', 'username', 'age', 'gender', 'phone', 'email', 'password', 'address', 'role']
        widgets = {
            'gender': forms.Select(attrs={'class': 'myInput'}),
            'role': forms.HiddenInput(),
        }

    def save(self, *args, **kwargs):
        cleaned_data = self.cleaned_data
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        email = cleaned_data.get('email')
        name = cleaned_data.get('name')
        role = cleaned_data.get('role')

        
        mod_user = None
        if ModeratorUser.objects.filter(email=email).exists():
            mod_user = ModeratorUser.objects.get(email=email)

        if mod_user:
            user = User.objects.get(email=email)
            user.username = username
            user.set_password(password)
            user.first_name = name
            user.email = email  
            user.save()

            mod_user.name = name
            mod_user.username = username
            mod_user.age = cleaned_data.get('age')
            mod_user.gender = cleaned_data.get('gender')
            mod_user.phone = cleaned_data.get('phone')
            mod_user.address = cleaned_data.get('address')
            mod_user.password = password
            #mod_user.role = role
            mod_user.save()
        else:
            if ModeratorUser.objects.filter(role=Role.ADMIN).count() == 0:
                user = User.objects.create_superuser(
                    username=username,
                    password=password,
                    email=email,
                    first_name=name
                )
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    first_name=name
                )
            user.save()
            instance = super().save(*args, **kwargs)
            return instance


class EmotionDataForm(forms.ModelForm):
    class Meta:
        model = EmotionData
        fields = ['date', 'happy', 'sad', 'surprise', 'angry', 'fear', 'neutral', 'processed_users']