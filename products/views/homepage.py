from django.shortcuts import render

def home(request):
    context = {
        "message": "Welcome to Django Templates"
    }
    return render(request, "base.html", context)