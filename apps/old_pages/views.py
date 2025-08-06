from django.http import HttpResponse


def home(request):
    return HttpResponse("Home page works.")


def ui(request):
    return HttpResponse("UI page works.")


def docs(request):
    return HttpResponse("Docs page works.")
