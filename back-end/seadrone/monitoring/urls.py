from django.urls import path
from . import views

urlpatterns = [
    # 分析页 - 水质数据API
    path('analysis/water-quality/', views.get_water_quality_data, name='water_quality_data'),
    path('analysis/nutrient/', views.get_nutrient_data, name='nutrient_data'),
    
    # 数据上传API（供无人船使用）
    path('upload/water-quality/', views.upload_water_quality_data, name='upload_water_quality'),
    path('upload/nutrient/', views.upload_nutrient_data, name='upload_nutrient'),
]
