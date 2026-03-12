from django.contrib import admin
from .models import WaterQualityData, NutrientData

@admin.register(WaterQualityData)
class WaterQualityDataAdmin(admin.ModelAdmin):
    list_display = ['ship_model', 'timestamp', 'temperature', 'pH', 'chlorophyll', 'warn', 'collection_time']
    list_filter = ['ship_model', 'warn', 'connection_status', 'collection_time']
    search_fields = ['ship_model']
    ordering = ['-collection_time']

@admin.register(NutrientData)
class NutrientDataAdmin(admin.ModelAdmin):
    list_display = ['ship_model', 'timestamp', 'status', 'phosphates', 'ammonia_nitrogen', 'nitrate', 'sub_nitrate', 'warn', 'collection_time']
    list_filter = ['ship_model', 'status', 'warn', 'collection_time']
    search_fields = ['ship_model']
    ordering = ['-collection_time']
