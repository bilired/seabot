# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('user/info/', views.user_info_view, name='user_info'),
    path('v3/system/menus/', views.menu_list_view, name='menu_list'),
    
    # 仪表板相关API
    path('dashboard/stats/', views.DashboardStatsView.as_view(), name='dashboard_stats'),
    path('dashboard/activity/', views.get_user_activity, name='user_activity'),
    path('dashboard/sales/', views.get_sales_data, name='sales_data'),
    path('dashboard/growth/', views.get_user_growth, name='user_growth'),
    
    # 分析页 - 水质数据API
    path('analysis/water-quality/', views.get_water_quality_data, name='water_quality_data'),
    path('analysis/nutrient/', views.get_nutrient_data, name='nutrient_data'),

    # 无人船设备管理
    path('drone/list/', views.get_drone_list, name='drone_list'),
    path('drone/create/', views.create_drone, name='drone_create'),
    path('drone/delete/', views.delete_drone, name='drone_delete'),
    path('drone/batch-delete/', views.batch_delete_drone, name='drone_batch_delete'),
    
    # 数据上传API（供无人船使用）
    path('upload/water-quality/', views.upload_water_quality_data, name='upload_water_quality'),
    path('upload/nutrient/', views.upload_nutrient_data, name='upload_nutrient'),
]