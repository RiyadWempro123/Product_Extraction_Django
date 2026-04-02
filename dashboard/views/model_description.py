from django.shortcuts import render

# Create your views here.
def ModelDescriptionChart(request):
    
    context = {
        "message": "Welcome to Django Templates"
    }
    return render(request, "dashboard/modelDescriptionChart.html", context)

def ModelDescriptionList(request):
    if request.method == "POST":
        
        data = request.POST
        print("Received JSON data:", data)
        # Get data from POST reques
        seriesName = request.POST.get("seriesName")
        seriesNumber = request.POST.get("seriesNumber")
    context = {
        "message": "Welcome to Django Templates"
    }
    return render(request, "dashboard/modelDescription_list.html", context)
    