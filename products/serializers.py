from rest_framework import serializers
from .models import PumpManual

class PumpManualSerializer(serializers.ModelSerializer):
    class Meta:
        model = PumpManual
        fields = ['id', 'brand', 'productSeries', 'modelName', 'pdfFile', 'created', 'updated']
