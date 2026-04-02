from django.shortcuts import render

# Create your views here.
def CommonParts(request):
    context = {
        "message": "Welcome to Django Templates"
    }
    return render(request, "dashboard/common_parts.html", context)