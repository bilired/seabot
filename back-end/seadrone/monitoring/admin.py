from django.contrib import admin
from .models import WaterQualityData, NutrientData

@admin.register(WaterQualityData)
class WaterQualityDataAdmin(admin.ModelAdmin):
    list_display = ['ship_model', 'temperature', 'ph', 'chlorophyll', 'warning_code', 'collection_time']
    list_filter = ['ship_model', 'warning_code', 'connection_status', 'collection_time']
    search_fields = ['ship_model']
    ordering = ['-collection_time']

@admin.register(NutrientData)
class NutrientDataAdmin(admin.ModelAdmin):
    list_display = ['ship_model', 'phosphate', 'ammonia', 'nitrate', 'instrument_status', 'collection_time']
    list_filter = ['ship_model', 'instrument_status', 'connection_status', 'collection_time']
    search_fields = ['ship_model']
    ordering = ['-collection_time']
