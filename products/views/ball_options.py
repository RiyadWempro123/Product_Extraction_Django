from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.conf import settings
from rest_framework import status
import os
from ..models import CommonParts, PumpManual, SeatOptions, BallOptions
from ..serializers import PumpManualSerializer

from utils import ball_options_data

class BallOptionsAPI(APIView):
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
            check_commonParts =  BallOptions.objects.filter(productSeries = productSeries).first()
            if check_commonParts:
                return Response({
                    "message": "File already exists",
                    "seat_options": "success"
                }, status=status.HTTP_200_OK)
            else:
                # extract_common_parts(pdf_file, page_number)
                ball_options = ball_options_data.extract_ball_options_from_pdf(file_path,pageNumber)
                if ball_options:
                    BallOptions.objects.create(
                        productSeries = productSeries, 
                        ballOptionJson = ball_options,
                        status="Y"
                        )
                    print('ball_options', ball_options)
                    
                    return Response({
                        "message": "File already exists",
                        "ball_options": ball_options
                    }, status=status.HTTP_200_OK)

        return Response({
            "message": "File does not exist",
            "path": file_path
        }, status=status.HTTP_200_OK)