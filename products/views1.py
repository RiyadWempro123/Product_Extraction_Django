from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.conf import settings
from rest_framework import status
import os
from .models import ModeldescriptionChart, CommonParts, PumpManual
from .serializers import PumpManualSerializer
from utils.model_description5 import extract_model_description_chart
from utils.common_parts1 import extract_common_parts




class PumpManualUploadAPI(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        print("Data", request.data)
        pdf_file = request.FILES.get("pdfFile")
        productSeries = request.data.get("productSeries")
        modelDescriptionChart = request.data.get("modelDescriptionChart")
       
        commonParts = request.data.get("commonParts")
        
        fluidConnection = request.data.get("fluidConnection")
        if fluidConnection:
            fluidConnectionPage = int(request.data.get("fluidConnectionPage"))
        airSectionParts = request.data.get("airSectionParts")
        if airSectionParts:
            airSectionPartsPage = int(request.data.get("airSectionPartsPage"))
        
        if not pdf_file:
            return Response({"error": "PDF required"}, status=400)

        # 1️⃣ Check existing PDF
        existing_pdf = PumpManual.objects.filter(pdfFile=pdf_file.name).first()
        if existing_pdf:
            return Response({
                "message": "PDF already exists. Using cached data.",
                "file": existing_pdf.pdfFile.name,
                "model_chart": existing_pdf.partsJson
            }, status=200)

        # 2️⃣ Save new PDF
        serializer = PumpManualSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

        pdf_path = obj.pdfFile.path

        # 3️⃣ Extract chart
        if modelDescriptionChart:
            modelDescriptionChartPage = int(request.data.get("modelDescriptionChartPage"))
            chart = extract_model_description_chart(pdf_path, modelDescriptionChartPage)

            if chart:
                ModeldescriptionChart.objects.get_or_create(
                    productSeries=productSeries,
                    defaults={
                        "modelSeries": chart.get("Model Series"),
                        "centerBodyMaterial": chart.get("Center Body Material"),
                        "fluidConnection": chart.get("Connection"),
                        "fluidCapsManifoldMaterial": chart.get("Fluid Caps / Manifold Material"),
                        "hardwareMaterial": chart.get("Hardware Material"),
                        "seatMaterial": chart.get("Seat / Spacer Material"),
                        "checkMaterial": chart.get("Check Material"),
                        "specialtyCode1": chart.get("Specialty Code 1"),
                        "specialtyCode2": chart.get("Specialty Code 2"),
                        "fileName":pdf_file
                    }
                )
            
            
                

            # extract_common_parts(pdf_path)
        if commonParts:
            commonPartsPage = int(request.data.get("commonPartsPage"))
            common_parts = extract_common_parts(pdf_path, commonPartsPage)
            print("common_parts", common_parts)
        # 4️⃣ Save JSON
        obj.partsJson = chart
        obj.save()

        return Response({
            "message": "PDF uploaded & model chart extracted",
            "file": obj.pdfFile.name,
            # "model_chart": chart,
            "common_parts":common_parts
        }, status=201)
        
  
