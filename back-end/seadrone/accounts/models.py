from django.db import models
from django.contrib.auth.models import User

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


class DroneDevice(models.Model):
    """无人船设备信息"""
    ship_type = models.CharField(max_length=50, help_text='船型')
    length = models.IntegerField(help_text='长度(cm)')
    model = models.CharField(max_length=50, help_text='型号')
    weight = models.FloatField(help_text='重量(kg)')
    functions = models.CharField(max_length=255, help_text='功能模块')
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


class WaterQualityData(models.Model):
    """水质监测数据"""
    ship_model = models.CharField(max_length=50, help_text='船型号')
    temperature = models.FloatField(help_text='水温(°C)')
    ph = models.FloatField(help_text='pH值')
    chlorophyll = models.FloatField(help_text='叶绿素(μg/L)')
    salinity = models.FloatField(help_text='盐度')
    dissolved_oxygen = models.FloatField(help_text='溶解氧(mg/L)')
    conductivity = models.FloatField(help_text='电导率(μS/cm)')
    turbidity = models.FloatField(help_text='浊度(NTU)')
    algae = models.IntegerField(help_text='蓝绿藻(cells/mL)')
    warning_code = models.CharField(max_length=50, default='正常', help_text='警告码')
    collection_time = models.DateTimeField(auto_now_add=True, help_text='采集时间')
    connection_status = models.CharField(max_length=20, default='在线', help_text='连接状态')
    
    class Meta:
        verbose_name = '水质数据'
        verbose_name_plural = '水质数据'
        ordering = ['-collection_time']
    
    def __str__(self):
        return f"{self.ship_model} - {self.collection_time}"


class NutrientData(models.Model):
    """营养盐数据"""
    ship_model = models.CharField(max_length=50, help_text='船型号')
    phosphate = models.FloatField(help_text='磷酸盐(mg/L)')
    phosphate_time = models.DateTimeField(help_text='磷酸盐获取时间')
    ammonia = models.FloatField(help_text='氨氮')
    ammonia_time = models.DateTimeField(help_text='氨氮获取时间')
    nitrate = models.FloatField(help_text='硝酸盐')
    nitrate_time = models.DateTimeField(help_text='硝酸盐获取时间')
    nitrite = models.FloatField(help_text='亚硝酸盐')
    nitrite_time = models.DateTimeField(help_text='亚硝酸盐获取时间')
    error_code1 = models.CharField(max_length=10, default='00', help_text='错误码1')
    error_code2 = models.CharField(max_length=10, default='00', help_text='错误码2')
    instrument_status = models.CharField(max_length=20, default='正常', help_text='仪器状态')
    collection_time = models.DateTimeField(auto_now_add=True, help_text='采集时间')
    connection_status = models.CharField(max_length=20, default='在线', help_text='连接状态')
    
    class Meta:
        verbose_name = '营养盐数据'
        verbose_name_plural = '营养盐数据'
        ordering = ['-collection_time']
    
    def __str__(self):
        return f"{self.ship_model} - {self.collection_time}"
