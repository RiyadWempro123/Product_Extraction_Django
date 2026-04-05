
from django.contrib import admin
from django.urls import path
from .views import dashboard, model_list, series_entry, model_description, common_parts, seat_options, ball_options, air_sections



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
    
    path ("ballOptions/", ball_options.BallOptions, name = "ballOptions"),
    path ("ballOptionList/", ball_options.BallOptionList, name = "ballOptionList"),
    
    path ("airSections/", air_sections.AirSections, name = "airSections"),
    path ("airSectionsList/", air_sections.AirSectionsList, name = "airSectionsList"),
    
]