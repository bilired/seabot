from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.

class DashboardStats(models.Model):
    """仪表板统计数据模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dashboard_stats')
    total_tasks = models.IntegerField(default=0, help_text='总任务数')
    completed_tasks = models.IntegerField(default=0, help_text='完成的任务数')
    active_projects = models.IntegerField(default=0, help_text='活跃项目数')
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='总销售额')
    new_users_count = models.IntegerField(default=0, help_text='新用户数')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '仪表板统计'
        verbose_name_plural = '仪表板统计'
    
    def __str__(self):
        return f"{self.user.username} - Dashboard Stats"


class MonthlySalesData(models.Model):
    """月度销售数据"""
    month = models.CharField(max_length=10, help_text='月份 (例如: 1月, 2月)')
    sales = models.IntegerField(help_text='销售金额')
    
    class Meta:
        verbose_name = '月度销售数据'
        verbose_name_plural = '月度销售数据'
    
    def __str__(self):
        return f"{self.month}: {self.sales}"


class UserGrowthData(models.Model):
    """用户增长数据"""
    date = models.DateField(help_text='日期')
    new_users = models.IntegerField(help_text='新增用户数')
    active_users = models.IntegerField(help_text='活跃用户数')
    
    class Meta:
        verbose_name = '用户增长数据'
        verbose_name_plural = '用户增长数据'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.date}: 新增{self.new_users}, 活跃{self.active_users}"

class UserActivity(models.Model):
    """用户活动日志"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(
        max_length=50,
        choices=[
            ('login', '登录'),
            ('task_completed', '任务完成'),
            ('project_created', '项目创建'),
            ('file_uploaded', '文件上传'),
            ('other', '其他')
        ],
        default='other'
    )
    description = models.CharField(max_length=255, help_text='活动描述')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '用户活动'
        verbose_name_plural = '用户活动'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"


class UserProfile(models.Model):
    """用户扩展信息"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.CharField(max_length=500, blank=True, default='', help_text='头像URL')
    mobile = models.CharField(max_length=20, blank=True, default='', help_text='手机号')
    real_name = models.CharField(max_length=50, blank=True, default='', help_text='姓名')
    nick_name = models.CharField(max_length=50, blank=True, default='', help_text='昵称')
    gender = models.CharField(max_length=2, blank=True, default='', help_text='性别编码：1男 2女')
    address = models.CharField(max_length=255, blank=True, default='', help_text='地址')
    description = models.TextField(blank=True, default='', help_text='个人介绍')

    class Meta:
        verbose_name = '用户扩展信息'
        verbose_name_plural = '用户扩展信息'

    def __str__(self):
        return f"{self.user.username} - Profile"


class DroneDevice(models.Model):
    """无人船设备信息"""
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='drone_devices', null=True, blank=True)
    ship_type = models.CharField(max_length=50, help_text='船型')
    length = models.IntegerField(help_text='长度(cm)')
    model = models.CharField(max_length=50, help_text='型号')
    weight = models.FloatField(help_text='重量(kg)')
    functions = models.CharField(max_length=255, help_text='功能模块')
    image = models.CharField(max_length=500, blank=True, default='', help_text='设备照片URL')
    stream_url = models.CharField(max_length=500, blank=True, default='', help_text='直播拉流地址')
    status = models.CharField(
        max_length=20,
        choices=[('online', '在线'), ('offline', '离线')],
        default='offline',
        help_text='设备状态'
    )
    max_speed = models.FloatField(help_text='最高航速(节)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '无人船设备'
        verbose_name_plural = '无人船设备'
        ordering = ['-id']

    def __str__(self):
        return f"{self.model}"


class ImageTransferRecord(models.Model):
    """图像传输历史记录"""

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='image_transfer_records',
        null=True,
        blank=True,
        help_text='记录归属用户'
    )
    ship_model = models.CharField(max_length=50, default='未知型号', help_text='船型/设备型号')
    image_uid = models.CharField(max_length=64, unique=True, help_text='图片唯一标识')
    timestamp = models.DateTimeField(help_text='图片时间戳')
    image_format = models.CharField(max_length=16, default='jpg', help_text='图片格式')
    resolution = models.CharField(max_length=32, blank=True, default='', help_text='分辨率，例如1920x1080')
    file_size_mb = models.FloatField(default=0, help_text='文件大小(MB)')
    image_url = models.CharField(max_length=500, help_text='图片URL')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '图像传输记录'
        verbose_name_plural = '图像传输记录'
        ordering = ['-timestamp', '-id']

    def __str__(self):
        return f"{self.image_uid} ({self.ship_model})"
