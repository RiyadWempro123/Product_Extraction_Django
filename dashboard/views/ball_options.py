from django.shortcuts import render
from products.models import PumpManual
from utils import ball_options_data
import os
from django.conf import settings

# Create your views here.
def BallOptions(request):
    context = {
        "message": "Welcome to Django Templates"
    }
    return render(request, "dashboard/ball_options.html", context)

def BallOptionList(request):
    if request.method == "POST":
        
        data = request.POST
        print("Received JSON data:", data)
        # Get data from POST reques
        seriesName = request.POST.get("seriesName")
        seriesNumber = request.POST.get("seriesNumber")
        get_data = PumpManual.objects.filter(seriesName=seriesName, seriesNumber=seriesNumber).first()
        if get_data:
            pdf_file = get_data.fileName
            ball_options_Page = get_data.ballOptions
            print('pdf_file.....', pdf_file)
            if pdf_file:
        
                file_path = os.path.join(settings.BASE_DIR, "static/pdf", str(pdf_file))
                if os.path.exists(file_path):
                    print("✅ File found:", file_path)
                    get_seat_options = ball_options_data.extract_ball_options_from_pdf(file_path, int(ball_options_Page))
                    print("get_seat_options", get_seat_options)

                else:
                    print("❌ File not found in static/pdf folder")
                    file_url = None
                    print('Hlw world')
            # model_description.extract_model_description_chart()
        
    context = {
        "data": get_seat_options
    }
    print("context", context)
    return render(request, "dashboard/ball_option_list.html", context)