from django.shortcuts import render

# Create your views here.
def ModelList(request):
    context = {
        "message": "Welcome to Django Templates"
    }
    return render(request, "dashboard/series_entry.html", context)