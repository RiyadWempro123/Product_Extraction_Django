
from django.contrib import admin
from django.urls import path
from .views import dashboard, model_list, series_entry, model_description, common_parts, seat_options



urlpatterns = [
    path("", dashboard.home, name="dashboard"),   
    path("modelList/", model_list.ModelList, name="detailsInfo" ),
    path ("addModelDescription/", model_description.ModelDescriptionChart, name = "addModelDescription"),
    path ("modelDescriptionList/", model_description.ModelDescriptionList, name = "modelDescriptionList"),
    path ("seriesentry/", series_entry.SeriesEntry, name = "seriesentry"),
    path ("commonParts/", common_parts.CommonParts, name = "commonParts"),
    path ("commonPartList/", common_parts.CommonPartList, name = "commonPartList"),
    
    path ("seatOptions/", seat_options.SeatOptions, name = "seatOptions"),
    path ("seatOptionList/", seat_options.SeatOptionList, name = "seatOptionList"),
    
]