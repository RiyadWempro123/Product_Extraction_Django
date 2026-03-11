from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.conf import settings
from rest_framework import status
import os
from ..models import ModeldescriptionChart, CommonParts, PumpManual
from utils.model_description5 import extract_model_description_chart
from ..serializers import PumpManualSerializer

from utils import common_parts_final

class CommonPartsAPI(APIView):
    def post(self, request):

        pdf_file = request.FILES.get("pdfFile")

        if not pdf_file:
            return Response({"error": "PDF file required"}, status=status.HTTP_400_BAD_REQUEST)

        pageNumber = int(request.data.get("pageNumber", 1))

        # Full path: media/pdfs/filename.pdf
        file_path = os.path.join(settings.MEDIA_ROOT, "pdfs", pdf_file.name)

        print("Checking path:", file_path)

        if os.path.exists(file_path):
            # extract_common_parts(pdf_file, page_number)
            common_parts = common_parts_final.extract_common_parts(file_path,pageNumber)
            print('common_parts', common_parts)
            
            return Response({
                "message": "File already exists",
                "common_parts": common_parts
            }, status=status.HTTP_200_OK)

        return Response({
            "message": "File does not exist",
            "path": file_path
        }, status=status.HTTP_200_OK)