from django.db import models
from .storage import OverwriteStorage
# Create your models here.

import os

def pump_pdf_path(instance, filename):
    # This keeps the ORIGINAL filename
    return f"pdfs/{filename}"


class PumpManual(models.Model):
    brand = models.CharField(max_length=100)
    productSeries = models.CharField(max_length=100)
    modelName = models.CharField(max_length=100, blank=True)
    # pdfFile = models.FileField(upload_to=pump_pdf_path)
    pdfFile = models.FileField(
        upload_to=pump_pdf_path,
        storage=OverwriteStorage()
    )
    # partsJson = models.JSONField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "PumpManual"

    def __str__(self):
        return f"{self.brand} - {self.modelName}"

class ModeldescriptionChart(models.Model):
    productSeries = models.CharField(max_length=100)
    modelSeries = models.TextField(blank=True, null= True)
    centerBodyMaterial = models.TextField(blank=True, null = True)
    fluidConnection = models.TextField (blank=True, null = True)
    fluidCapsManifoldMaterial = models.TextField (blank=True, null = True)
    hardwareMaterial = models.TextField(blank=True, null= True)
    seatMaterial = models.TextField(blank=True, null = True)
    checkMaterial = models.TextField (blank=True, null = True)
    specialtyCode1 = models.TextField (blank=True, null = True)
    specialtyCode2 = models.TextField(blank=True, null= True)
    specialTesting = models.TextField (blank=True, null = True)
    fileName  = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "ModeldescriptionChart"

    def __str__(self):
        return f"{self.modelSeries} - {self.productSeries}"


class CommonParts(models.Model):
    productSeries = models.CharField(max_length=100)
    commonPartJson = models.TextField(blank=True, null = True)
    status = models.CharField(max_length=1, default="N")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "CommonParts"

    def __str__(self):
        return f"{self.productSeries}"

class SeatOptions(models.Model):
    productSeries = models.CharField(max_length=100)
    seatOptionJson = models.TextField(blank=True, null = True)
    status = models.CharField(max_length=1, default="N")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    
    class Meta:
        db_table = "SeatOptions"

    def __str__(self):
        return f"{self.productSeries}"
    
    
class BallOptions(models.Model):
    productSeries = models.CharField(max_length=100)
    ballOptionJson = models.TextField(blank=True, null = True)
    brand = models.CharField(max_length=30, blank=True, null=True)
    status = models.CharField(max_length=1, default="N")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    
    class Meta:
        db_table = "BallOptions"

    def __str__(self):
        return f"{self.productSeries}"