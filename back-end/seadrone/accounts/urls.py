# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('register/sms/send/', views.send_register_sms_code_view, name='register_sms_send'),
    path('register/sms/verify/', views.verify_register_sms_code_view, name='register_sms_verify'),
    path('user/password/sms/send/', views.send_change_password_sms_code_view, name='change_password_sms_send'),
    path('user/password/sms/verify/', views.verify_change_password_sms_code_view, name='change_password_sms_verify'),
    path('user/password/change/', views.change_password_view, name='change_password'),
    path('login/', views.login_view, name='login'),
    path('user/info/', views.user_info_view, name='user_info'),
    path('user/profile/update/', views.update_user_profile_view, name='user_profile_update'),
    path('user/avatar/upload/', views.upload_user_avatar, name='user_avatar_upload'),
    path('user/list/', views.get_user_list, name='user_list'),
    path('user/create/', views.create_user, name='user_create'),
    path('user/update/', views.update_user, name='user_update'),
    path('user/delete/', views.delete_user, name='user_delete'),
    path('v3/system/menus/', views.menu_list_view, name='menu_list'),
    
    # 仪表板相关API
    path('dashboard/stats/', views.DashboardStatsView.as_view(), name='dashboard_stats'),
    path('dashboard/activity/', views.get_user_activity, name='user_activity'),
    path('dashboard/sales/', views.get_sales_data, name='sales_data'),
    path('dashboard/growth/', views.get_user_growth, name='user_growth'),
    
    # 无人船设备管理
    path('drone/list/', views.get_drone_list, name='drone_list'),
    path('drone/create/', views.create_drone, name='drone_create'),
    path('drone/update/', views.update_drone, name='drone_update'),
    path('drone/upload-image/', views.upload_drone_image, name='drone_upload_image'),
    path('drone/delete/', views.delete_drone, name='drone_delete'),
    path('drone/batch-delete/', views.batch_delete_drone, name='drone_batch_delete'),
    path('drone/image-history/list/', views.get_image_transfer_history, name='image_transfer_history_list'),
    path('drone/image-history/delete/', views.delete_image_transfer_record, name='image_transfer_history_delete'),
    path('drone/image-history/batch-delete/', views.batch_delete_image_transfer_records, name='image_transfer_history_batch_delete'),
]