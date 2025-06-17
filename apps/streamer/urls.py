from django.urls import path

from . import views
from .views import streamer_home

urlpatterns = [
    path("camera/", views.camera_input, name="camera_input"),
    path("mic/", views.mic_input, name="mic_input"),
    path("", streamer_home, name="streamer_home"),
]
