# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('user/info/', views.user_info_view, name='user_info'),
    path('v3/system/menus/', views.menu_list_view, name='menu_list'),
]