from django.shortcuts import render, redirect
from django.http import JsonResponse
from .camera import camera
from .forms import ModeratorUserForm
from .models import ModeratorUser, Role
from .models import EmotionData
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
import json
from datetime import datetime


MAX_ADMINS = 1


def is_admin(request):
    user = request.user
    is_admin_ = False
    if user.is_authenticated:
        moderator_user = ModeratorUser.objects.filter(email=user.email).first()
        if moderator_user and moderator_user.role == Role.ADMIN:
            is_admin_ = True
    return is_admin_

def home(request):
    valid = is_admin(request) or not request.user.is_authenticated
    admins = ModeratorUser.objects.filter(role=Role.ADMIN).count()
    return render(request, 'home.html', {'is_admin': valid, 'admins': admins})

@login_required
def analyze(request):
    return render(request, 'analyze.html', {'is_admin': is_admin(request)})

@login_required
def video_feed(request):
    try:
        frame = camera.get_frame()
        emotions = camera.last_emotions
        camera.update_emotion_data(emotions, request.user)
        if emotions:
            return JsonResponse({'image': frame,
                                 'happy': emotions[0].get('happy'),
                                 'anger': emotions[0].get('angry'),
                                 'surprise': emotions[0].get('surprise'),
                                 'nature': emotions[0].get('neutral'),
                                 'fear': emotions[0].get('fear'),
                                 'sad': emotions[0].get('sad')
                                 })
        else:
            return JsonResponse({'image': frame, 'happy': None, 'sad': None})
    except Exception as e:
        print(e)
        return JsonResponse({'error': 'Failed to fetch data'})

@login_required
def profile(request):
    user = request.user
    try:
        email = user.email
        user = ModeratorUser.objects.get(email=email)
    except:
        pass
    return render(request, 'profile.html', {'user': user, 'is_admin': is_admin(request), 'id': user.id})

def allow_if_no_admins(user):
    no_admin_users = not ModeratorUser.objects.filter(role=Role.ADMIN).exists()
    is_authenticated = user.is_authenticated
    return no_admin_users or is_authenticated

def allow_if_admin_only(user):
    if not user.is_authenticated:
        return True
    is_admin = ModeratorUser.objects.filter(email=user.email, role=Role.ADMIN).exists()
    return is_admin

@user_passes_test(allow_if_no_admins)
@user_passes_test(allow_if_admin_only)
def addModerator(request):
    admins = ModeratorUser.objects.filter(role=Role.ADMIN).count()
    form = ModeratorUserForm()
    user = None
    if request.method == 'POST':
        form = ModeratorUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        action = request.GET.get('action')
        if not action or action not in ['view', 'edit']:
            return redirect('/')
        if admins == 0:
            return render(request, 'addModerator.html', {'form': form, 'admins': admins, 'max_admins': MAX_ADMINS, 'is_admin': is_admin(request)})
        email = request.user.email
        if action == 'edit':
            email = request.GET.get('email')
            try:
                user = ModeratorUser.objects.get(email=email)
            except User.DoesNotExist:
                return redirect('/')  
            form = ModeratorUserForm(instance=user)
    return render(request, 'addModerator.html', {'form': form, 'users': admins, 'max_admins': MAX_ADMINS, 'is_admin': is_admin(request), 'action': action, 'user': user})


@login_required
def viewData(request):
    all_dates = EmotionData.objects.values_list('date', flat=True).distinct().order_by('date')
    emotion_data_for_dates = []

    for date in all_dates:
        emotion_data = EmotionData.objects.filter(date=date).first()
        emotion_data_dict = {
            'date': date.strftime('%Y-%m-%d'),  # Format date as string
            'emotion_data': {
                'happy': emotion_data.happy,
                'sad': emotion_data.sad,
                'angry': emotion_data.angry,
                'surprise': emotion_data.surprise,
                'neutral': emotion_data.neutral,
                'fear': emotion_data.fear
            }
        }

        emotion_data_for_dates.append(emotion_data_dict)

    emotion_data_json_str = json.dumps(emotion_data_for_dates)
    return render(request, 'viewEmotionData.html', {'emotion_data_for_dates_json': emotion_data_json_str, 'is_admin': is_admin(request)})

@login_required
def calendar(request):
    return render(request, 'calendar.html', {'is_admin': is_admin(request)})

@user_passes_test(allow_if_admin_only)
def exportData(request):
    selected_date_str = request.GET.get('selected_date')
    if not selected_date_str:
        return redirect('calendar') 
    selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d')
    emotion_data = EmotionData.objects.filter(date=selected_date).first()
    emotion_data_dict = {
        'date': selected_date.strftime('%Y-%m-%d'),  
        'emotion_data': {
            'happy': emotion_data.happy if emotion_data else 0,
            'sad': emotion_data.sad if emotion_data else 0,
            'angry': emotion_data.angry if emotion_data else 0,
            'surprise': emotion_data.surprise if emotion_data else 0,
            'neutral': emotion_data.neutral if emotion_data else 0,
            'fear': emotion_data.fear if emotion_data else 0
        }
    }
    emotion_data_for_dates = [emotion_data_dict]

    emotion_data_json_str = json.dumps(emotion_data_for_dates)

    return render(request, 'exportData.html', {'selected_date': selected_date, 'emotion_data_for_dates_json': emotion_data_json_str, 'is_admin': is_admin(request)})

@user_passes_test(allow_if_admin_only)
def show_users(request):
    users = ModeratorUser.objects.all()
    return render(request, 'users.html', {'is_admin': is_admin(request), 'users': users})

@user_passes_test(allow_if_admin_only)
def show_emotions(request):
    emotions = EmotionData.objects.all()
    return render(request, 'emotions.html', {'is_admin': is_admin(request), 'emotions': emotions})

@user_passes_test(allow_if_admin_only)
def processed_users(request):
    date_ = request.GET.get('date')
    date = datetime.strptime(date_, '%B %d, %Y').strftime('%Y-%m-%d')
    emails = []
    try:
        emotionsList = EmotionData.objects.filter(date=date)
        emails_str = emotionsList[0].processed_users
        emails = emails_str.split(',')
    except:
        pass
    users = []
    for email in emails:
        try:
            users.append(ModeratorUser.objects.get(email=email))
        except:
            pass
    return render(request, 'processed_users.html', {'is_admin': is_admin(request), 'users': users})