from django.shortcuts import render, redirect
from django.http import JsonResponse
from .camera import camera
from .forms import ModeratorUserForm
from .models import ModeratorUser
from .models import EmotionData
from django.contrib.auth.decorators import login_required
import json
from datetime import datetime


@login_required
def home(request):
    return render(request, 'home.html', {})

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
    return render(request, 'profile.html', {'user': user})

@login_required
def addModerator(request):
    if request.method == 'POST':
        form = ModeratorUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ModeratorUserForm()
    return render(request, 'addModerator.html', {'form': form})

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
    return render(request, 'viewEmotionData.html', {'emotion_data_for_dates_json': emotion_data_json_str})

@login_required
def calendar(request):
    return render(request, 'calendar.html', {})

@login_required
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

    return render(request, 'exportData.html', {'selected_date': selected_date, 'emotion_data_for_dates_json': emotion_data_json_str})