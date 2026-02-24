from django.db import models

# Create your models here.

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
