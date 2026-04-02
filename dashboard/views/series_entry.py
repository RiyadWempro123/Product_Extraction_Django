from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import json
from products.models import PumpManual
import os
from django.conf import settings

# Create your views here.
def ModelDescriptionChart(request):
    context = {
        "message": "Welcome to Django Templates"
    }
    return render(request, "dashboard/modelDescriptionChart.html", context)



# Import your model if you want to save data
# from .models import Brand  

def SeriesEntry(request):
    if request.method == "POST":
        
        data = request.POST
        print("Received JSON data:", data)
        # Get data from POST request
        brandName = request.POST.get("brandName")
        seriesName = request.POST.get("seriesName")
        seriesNumber = request.POST.get("seriesNumber")
        fileName = request.POST.get("fileName")
        modelDescriptionChart = request.POST.get("modelDescriptionChart")
        commonParts = request.POST.get("commonParts")
        seatOptions = request.POST.get("seatOptions") 
        ballOptions = request.POST.get("ballOptions")  
        airMotorSections = request.POST.get("airMotorSections")
        PumpManual.objects.create(
            brandName = brandName,
            seriesName = seriesName,
            seriesNumber = seriesNumber,
            fileName = fileName,
            modelDescriptionChart = modelDescriptionChart,
            commonParts = commonParts,
            seatOptions = seatOptions,
            ballOptions = ballOptions,
            airMotorSections = airMotorSections  
            
        )
        print("Brand Name", brandName)
        print("brand_category", seriesName)
        print("seriesNumber", seriesNumber)
        

        message = {
            "brandName":brandName,
            "seriesName":seriesName
        }
        context = {"message": message}
        return render(request, "dashboard/info.html", context)

    # If GET request, just render empty form or default message
    context = {"message": "Welcome to Django Templates"}
    return render(request, "dashboard/info.html", context)




def SeriesEntry(request):
    if request.method == "POST":

        brandName = request.POST.get("brandName")
        seriesName = request.POST.get("seriesName")
        seriesNumber = request.POST.get("seriesNumber")

        pdf_file = request.FILES.get("fileName")

        modelDescriptionChart = request.POST.get("modelDescriptionChart")
        commonParts = request.POST.get("commonParts")
        seatOptions = request.POST.get("seatOptions")
        ballOptions = request.POST.get("ballOptions")
        airMotorSections = request.POST.get("airMotorSections")
        print("pdf_file...........................", pdf_file)
        saved_filename = None

        if pdf_file:
            static_pdf_path = os.path.join(settings.BASE_DIR, "static/pdf")

            # Create folder if not exists
            if not os.path.exists(static_pdf_path):
                os.makedirs(static_pdf_path)

            file_path = os.path.join(static_pdf_path, pdf_file.name)

            # 🔍 Check if file already exists
            if os.path.exists(file_path):
                print("File already exists:", pdf_file.name)
                saved_filename = pdf_file.name
            else:
                # Save file
                with open(file_path, "wb+") as destination:
                    for chunk in pdf_file.chunks():
                        destination.write(chunk)

                print("File saved:", pdf_file.name)
                saved_filename = pdf_file.name

        # Save to database
        PumpManual.objects.create(
            brandName=brandName,
            seriesName=seriesName,
            seriesNumber=seriesNumber,
            fileName=saved_filename,
            modelDescriptionChart=modelDescriptionChart,
            commonParts=commonParts,
            seatOptions=seatOptions,
            ballOptions=ballOptions,
            airMotorSections=airMotorSections
            
        )

        context = {
            "message": {
                "brandName": brandName,
                "seriesName": seriesName,
                "seriesNumber": seriesNumber,
                "fileName": saved_filename,
                "modelDescriptionChart": modelDescriptionChart,
                "commonParts": commonParts,
                "seatOptions": seatOptions,
                "ballOptions": ballOptions,
                "airMotorSections": airMotorSections
            }
        }


        return render(request, "dashboard/info.html", context)

    return render(request, "dashboard/info.html", {"message": "Welcome"})