from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.conf import settings
from rest_framework import status
import os
from ..models import ModeldescriptionChart, CommonParts, PumpManual
from utils.model_description5 import extract_model_description_chart
from ..serializers import PumpManualSerializer

class ModelDescriptionAPI(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request):
        data = request.data  
        print ('data from frontend', data)
        pdf_file = request.FILES.get("pdfFile")
        pageNumber = int(request.data.get("pageNumber"))
        productSeries = request.data.get("productSeries")
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

        chart = extract_model_description_chart(pdf_path, pageNumber)
        
        print ("Chart", chart )

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
        
        return Response ({"results": chart}, status=status.HTTP_201_CREATED)


class ModelDescriptionAPI(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        data = request.data
        print("data from frontend", data)

        pdf_file = request.FILES.get("pdfFile")
        pageNumber = int(request.data.get("pageNumber"))
        productSeries = request.data.get("productSeries")

        if not pdf_file:
            return Response({"error": "PDF required"}, status=400)

        # 1️⃣ Check if PDF already exists
        print ("pdf_file.name",pdf_file.name)
        existing_pdf = PumpManual.objects.filter(pdfFile__endswith=pdf_file.name).first()

        if existing_pdf:
            return Response({
                "message": "PDF already exists. Using cached data.",
                "file": existing_pdf.pdfFile.name,
                # "model_chart": existing_pdf.partsJson
            }, status=200)

        # 2️⃣ Save new PDF ONLY if it does not exist
        serializer = PumpManualSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

        pdf_path = obj.pdfFile.path

        # 3️⃣ Extract chart data
        chart = extract_model_description_chart(pdf_path, pageNumber)

        print("Chart", chart)

        # 4️⃣ Save chart if data exists
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
                    "fileName": obj.pdfFile.name
                }
            )

        return Response({"results": chart}, status=status.HTTP_201_CREATED)

