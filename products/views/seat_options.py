from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.conf import settings
from rest_framework import status
import os
from ..models import ModeldescriptionChart, CommonParts, PumpManual, SeatOptions
from utils.model_description5 import extract_model_description_chart
from ..serializers import PumpManualSerializer

from utils import seat_options_data

class SeatOptionsAPI(APIView):
    def post(self, request):

        pdf_file = request.FILES.get("pdfFile")

        if not pdf_file:
            return Response({"error": "PDF file required"}, status=status.HTTP_400_BAD_REQUEST)

        pageNumber = int(request.data.get("pageNumber", 1))
        productSeries = request.data.get("productSeries")

        # Full path: media/pdfs/filename.pdf
        file_path = os.path.join(settings.MEDIA_ROOT, "pdfs", pdf_file.name)

        print("Checking path:", file_path)

        if os.path.exists(file_path):
            check_commonParts =  SeatOptions.objects.filter(productSeries = productSeries).first()
            if check_commonParts:
                return Response({
                    "message": "File already exists",
                    "seat_options": "success"
                }, status=status.HTTP_200_OK)
            else:
                # extract_common_parts(pdf_file, page_number)
                seat_options = seat_options_data.extract_seat_options_from_pdf(file_path,pageNumber)
                if seat_options:
                    SeatOptions.objects.create(
                        productSeries = productSeries, 
                        seatOptionJson = seat_options,
                        status="Y"
                        )
                    print('seat_options', seat_options)
                    
                    return Response({
                        "message": "File already exists",
                        "seat_options": seat_options
                    }, status=status.HTTP_200_OK)

        return Response({
            "message": "File does not exist",
            "path": file_path
        }, status=status.HTTP_200_OK)