from django.shortcuts import render
from products.models import PumpManual
from utils import common_parts_final
import os
from django.conf import settings

# Create your views here.
def CommonParts(request):
    context = {
        "message": "Welcome to Django Templates"
    }
    return render(request, "dashboard/common_parts.html", context)

def CommonPartList(request):
    if request.method == "POST":
        
        data = request.POST
        print("Received JSON data:", data)
        # Get data from POST reques
        seriesName = request.POST.get("seriesName")
        seriesNumber = request.POST.get("seriesNumber")
        get_data = PumpManual.objects.filter(seriesName=seriesName, seriesNumber=seriesNumber).first()
        if get_data:
            pdf_file = get_data.fileName
            commonPartPage = get_data.commonParts
            print('pdf_file.....', pdf_file)
            if pdf_file:
        
                file_path = os.path.join(settings.BASE_DIR, "static/pdf", str(pdf_file))
                if os.path.exists(file_path):
                    print("✅ File found:", file_path)
                    get_common_parts = common_parts_final.extract_common_parts(file_path, int(commonPartPage))
                    print("get_common_parts", get_common_parts)

                else:
                    print("❌ File not found in static/pdf folder")
                    file_url = None
            # model_description.extract_model_description_chart()
        
    context = {
        "data": get_common_parts
    }
    print("context", context)
    return render(request, "dashboard/common_part_list.html", context)
    