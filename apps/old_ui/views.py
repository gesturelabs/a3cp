from django.shortcuts import render


def landing_view(request):
    return render(request, "landing.html")


def demonstrator_view(request):
    return render(request, "demonstrator.html")
