import time
import cv2
from deepface import DeepFace
import base64
import threading
from .forms import EmotionDataForm
from .models import EmotionData
from django.utils import timezone

class VideoCamera(object):
    def __init__(self):
        self.frame = None
        self.video = None
        self.backends = [cv2.CAP_ANY, cv2.CAP_DSHOW, cv2.CAP_VFW, cv2.CAP_FFMPEG]
        self.selected_backend = None
        self.initialize_camera()
        if self.video is None or not self.video.isOpened():
            raise RuntimeError("Error: Unable to open camera.")
        self.lock = threading.Lock()
        self.analyze_counter = 0
        self.last_emotions = []
        threading.Thread(target=self.update, args=()).start()

    def initialize_camera(self):
        for backend in self.backends:
            self.video = cv2.VideoCapture(0, backend)
            if self.video.isOpened():
                self.selected_backend = backend
                break

    def __del__(self):
        self.video.release()

    def get_frame(self):
        with self.lock:
            if self.frame is not None:
                ret, jpeg = cv2.imencode('.jpg', self.frame)
                if ret:
                    return base64.b64encode(jpeg.tobytes()).decode('utf-8')
        return None

    def update(self):
        while True:
            ret, frame = self.video.read()
            if ret:
                if not frame.size == 0:
                    with self.lock:
                        self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        self.analyze_counter += 1
                        if self.analyze_counter == 10:
                            self.analyze_counter = 0
                            self.last_emotions = self.analyze_frame(self.frame)
                else:
                    print("Warning: Empty frame received.")
            else:
                print("Error: Failed to read frame. Retrying...")
                with self.lock:
                    self.frame = None 
                self.initialize_camera()  
                time.sleep(1) 

    def analyze_frame(self, frame):
        try:
            result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            emotions = [item['emotion'] for item in result]
            for i in range(len(emotions)):
                emotions[i] = {key: int(value) for key, value in emotions[i].items()}
            return emotions
        except Exception as e:
            print("Error analyzing frame:", e)
            return []
        
    def update_emotion_data(self, emotions, user):
        today = timezone.localdate()
        emotion_data, created = EmotionData.objects.get_or_create(date=today)
        if emotion_data.already_processed(user.email):
            return
        highestEmotion = None
        highestValue = 0
        if emotions:
            for key, value in emotions[0].items():
                if value > highestValue:
                    highestValue = value
                    highestEmotion = key
        if highestValue != 0:
            emotion_data.add_processed_user(user.email)
            setattr(emotion_data, highestEmotion, getattr(emotion_data, highestEmotion) + 1)
            emotion_data.save()
        
camera = VideoCamera()