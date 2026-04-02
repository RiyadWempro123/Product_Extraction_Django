from django.shortcuts import render

# Create your views here.
def home(request):
    context = {
        "message": "Welcome to Django Templates"
    }
    return render(request, "layouts/base.html", context)