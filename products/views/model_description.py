from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.conf import settings
from rest_framework import status
import os
from models import ModeldescriptionChart, CommonParts, PumpManual

class ModelDescriptionAPI(APIView):
    def post(self, request):
        data = request.data  
        print ('data from frontend', data)
        
        return Response ({"results":data}, status=status.HTTP_201_CREATED)
        