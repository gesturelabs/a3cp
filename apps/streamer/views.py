from django.shortcuts import render
from django.http import HttpResponse

def camera_input(request):
    return HttpResponse("Camera input placeholder.")

def mic_input(request):
    return HttpResponse("Microphone input placeholder.")

def streamer_home(request):
    return HttpResponse("Streamer module placeholder: camera and mic input will go here.")

