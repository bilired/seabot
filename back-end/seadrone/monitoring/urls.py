from django.urls import path
from . import views

urlpatterns = [
    # 分析页 - 水质数据API
    path('analysis/water-quality/', views.get_water_quality_data, name='water_quality_data'),
    path('analysis/nutrient/', views.get_nutrient_data, name='nutrient_data'),
    path('analysis/video-stream/', views.get_video_stream_data, name='video_stream_data'),
    
    # 数据上传API（供无人船使用）
    path('upload/water-quality/', views.upload_water_quality_data, name='upload_water_quality'),
    path('upload/nutrient/', views.upload_nutrient_data, name='upload_nutrient'),
    path('upload/video-stream/', views.upload_video_stream_data, name='upload_video_stream'),
    path('upload/ship-packet/', views.upload_ship_packet_data, name='upload_ship_packet'),

    # 连接服务网关 API
    path('ship/gateway/start/', views.ship_gateway_start, name='ship_gateway_start'),
    path('ship/gateway/status/', views.ship_gateway_status, name='ship_gateway_status'),
    path('ship/device-status/', views.device_status, name='device_status'),
    path('ship/device-locations/', views.device_locations, name='device_locations'),
    path('ship/track/history/', views.ship_track_history, name='ship_track_history'),
    path('ship/action/', views.ship_action, name='ship_action'),
]
