from django.shortcuts import render

# Create your views here.
def SeatOptions(request):
    context = {
        "message": "Welcome to Django Templates"
    }
    return render(request, "dashboard/seat_options.html", context)