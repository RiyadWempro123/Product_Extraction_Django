from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.conf import settings
from rest_framework import status
import os
from ..models import CommonParts, PumpManual, SeatOptions, BallOptions, AirMotorOptions
from ..serializers import PumpManualSerializer

from utils import air_motor_data

class AirMotorOptionsAPI(APIView):
    def post(self, request):

        pdf_file = request.FILES.get("pdfFile")

        if not pdf_file:
            return Response({"error": "PDF file required"}, status=status.HTTP_400_BAD_REQUEST)

        pageNumber = int(request.data.get("pageNumber", 1))
        productSeries = request.data.get("productSeries")
        print("productSeries", productSeries)

        # Full path: media/pdfs/filename.pdf
        file_path = os.path.join(settings.MEDIA_ROOT, "pdfs", pdf_file.name)

        print("Checking path:", file_path)

        if os.path.exists(file_path):
            check_airParts =  AirMotorOptions.objects.filter(productSeries = productSeries).first()
            if check_airParts:
                return Response({
                    "message": "File already exists",
                    "seat_options": "success"
                }, status=status.HTTP_200_OK)
            else:
                # extract_common_parts(pdf_file, page_number)
                air_motor_options = air_motor_data.extract_from_pdf(file_path,pageNumber)
                if air_motor_options:
                    BallOptions.objects.create(
                        productSeries = productSeries, 
                        ballOptionJson = air_motor_options,
                        status="Y"
                        )
                    print('ball_options', air_motor_options)
                    
                    return Response({
                        "message": "File already exists",
                        "air_motor_options": air_motor_options
                    }, status=status.HTTP_200_OK)

        return Response({
            "message": "File does not exist",
            "path": file_path
        }, status=status.HTTP_200_OK)