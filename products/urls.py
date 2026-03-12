
from django.contrib import admin
from django.urls import path
from . import views1
from .views import model_description, common_parts, seat_options


urlpatterns = [
    path('home/', views1.PumpManualUploadAPI.as_view(), name = "home"),
    path("modeldescription/", model_description.ModelDescriptionAPI.as_view(), name="modeldescription"),
    path("commonparts/", common_parts.CommonPartsAPI.as_view(), name="commonparts"),
    path("seatoptions/", seat_options.SeatOptionsAPI.as_view(), name="seatoptions"),
    
]