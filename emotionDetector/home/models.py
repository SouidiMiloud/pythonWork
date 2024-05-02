from django.db import models
from django.utils.translation import gettext as _


class Gender(models.TextChoices):
    MALE = 'M', _('Male')
    FEMALE = 'F', _('Female')

class Role(models.TextChoices):
    MODERATOR = 'M', _('Moderator')
    ADMIN = 'A', _('Admin')

class ModeratorUser(models.Model):
    name = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=1, choices=Gender.choices, default=Gender.MALE)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    password = models.CharField(max_length=200)
    address = models.TextField()
    role = models.CharField(max_length=1, choices=Role.choices, default=Role.MODERATOR)


class EmotionData(models.Model):
    date = models.DateField()
    happy = models.IntegerField(default=0)
    sad = models.IntegerField(default=0)
    surprise = models.IntegerField(default=0)
    angry = models.IntegerField(default=0)
    fear = models.IntegerField(default=0)
    neutral = models.IntegerField(default=0)
    processed_users = models.TextField(default="")

    def add_processed_user(self, user_email):
        if not self.already_processed(user_email):
            if self.processed_users:
                self.processed_users += f",{user_email}"
            else:
                self.processed_users = user_email
            self.save()

    def already_processed(self, user_email):
        return user_email in self.processed_users.split(',')
    
    def get_emotion_data(self):
        return {
            'happy': self.happy,
            'sad': self.sad,
            'surprise': self.surprise,
            'angry': self.angry,
            'fear': self.fear,
            'neutral': self.neutral
        }