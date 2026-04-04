from django.shortcuts import render
from products.models import PumpManual
from utils import model_description
import os
from django.conf import settings

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
        get_data = PumpManual.objects.filter(seriesName=seriesName, seriesNumber=seriesNumber).first()
        if get_data:
            pdf_file = get_data.fileName
            modelDescriptionPage = get_data.modelDescriptionChart
            print('pdf_file.....', pdf_file)
            if pdf_file:
        
                file_path = os.path.join(settings.BASE_DIR, "static/pdf", str(pdf_file))
                if os.path.exists(file_path):
                    print("✅ File found:", file_path)
                    get_model_description = model_description.extract_model_description_chart(file_path, int(modelDescriptionPage))
                    print("get_model_description", get_model_description)

                else:
                    print("❌ File not found in static/pdf folder")
                    file_url = None
            # model_description.extract_model_description_chart()
        
    context = {
        "data": get_model_description
    }
    print("context", context)
    return render(request, "dashboard/modelDescription_list.html", context)
    