
from django.contrib import admin
from django.urls import path
from .views import dashboard, model_list, series_entry, model_description, common_parts, seat_options, ball_options, air_sections



urlpatterns = [
    path("", dashboard.home, name="dashboard"),   
    path("modelList/", model_list.ModelList, name="detailsInfo" ),
    path ("model-description-entry/", model_description.ModelDescriptionChart, name = "addModelDescription"),
    path ("model-description-save/", model_description.ModelDescriptionList, name = "modelDescriptionList"),
    path('model-description-view/<str:seriesNumber>/', model_description.ModelDescriptionView, name='model-description-view'),
    path ('series-list/', series_entry.SeriesList, name = "seriesList"),
    path('series-detail/<str:seriesNumber>/', series_entry.SeriesDetail, name='series-detail'),
    # path('model-description-edit/', model_description.ModelDescriptionEdit, name='modelDescriptionEdit'),
    # path('model-description-delete/', model_description.ModelDescriptionDelete, name='modelDescriptionDelete'),
    
    path ("seriesentry/", series_entry.SeriesEntry, name = "seriesentry"),
    path ("common-parts-entry/", common_parts.CommonPartsEntry, name = "commonParts"),
    path ("common-parts-save/", common_parts.CommonPartListSave, name = "commonPartList"),
    path('common-parts-view/<str:seriesNumber>/', common_parts.CommonPartView, name='common-parts-view'),
    
    path ("seatOptions/", seat_options.SeatOptions, name = "seatOptions"),
    path ("seatOptionList/", seat_options.SeatOptionList, name = "seatOptionList"),
    
    path ("ballOptions/", ball_options.BallOptions, name = "ballOptions"),
    path ("ballOptionList/", ball_options.BallOptionList, name = "ballOptionList"),
    
    path ("airSections/", air_sections.AirSections, name = "airSections"),
    path ("airSectionsList/", air_sections.AirSectionsList, name = "airSectionsList"),
    
]