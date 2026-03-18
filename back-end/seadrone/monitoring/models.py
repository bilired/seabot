from django.db import models

# Create your models here.

class WaterQualityData(models.Model):
    """水质监测数据"""
    ship_model = models.CharField(max_length=50, help_text='船型号')
    timestamp = models.DateTimeField(null=True, blank=True, db_index=True, help_text='时间戳')
    temperature = models.FloatField(help_text='水温(°C)')
    pH = models.FloatField(help_text='pH值')
    chlorophyll = models.FloatField(help_text='叶绿素(μg/L)')
    salinity = models.FloatField(help_text='盐度')
    dissolved_oxygen = models.FloatField(help_text='溶解氧(mg/L)')
    conductivity = models.FloatField(help_text='电导率(μS/cm)')
    turbidity = models.FloatField(help_text='浊度(NTU)')
    blue_green = models.FloatField(help_text='蓝绿藻(cells/mL)')
    warn = models.CharField(max_length=50, default='0', help_text='警告码，默认0')
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
    ship_model = models.CharField(max_length=50, help_text='数据唯一标识(data_id)')
    timestamp = models.DateTimeField(null=True, blank=True, db_index=True, help_text='时间戳')
    status = models.IntegerField(default=0, help_text='0未连接，1已连接')
    ammonia_nitrogen = models.FloatField(help_text='氨氮(mg/L)')
    ammonia_nitrogen_timestamp = models.DateTimeField(help_text='氨氮获取时间')
    nitrate = models.FloatField(help_text='硝酸盐')
    nitrate_timestamp = models.DateTimeField(help_text='硝酸盐获取时间')
    sub_nitrate = models.FloatField(help_text='亚硝酸盐(mg/L)')
    sub_nitrate_timestamp = models.DateTimeField(help_text='亚硝酸盐获取时间')
    phosphates = models.FloatField(help_text='磷酸盐(mg/L)')
    phosphates_timestamp = models.DateTimeField(help_text='磷酸盐获取时间')
    warn = models.CharField(max_length=50, default='0', help_text='警告码，默认0')
    collection_time = models.DateTimeField(auto_now_add=True, help_text='采集时间')
    
    class Meta:
        verbose_name = '营养盐数据'
        verbose_name_plural = '营养盐数据'
        ordering = ['-collection_time']
    
    def __str__(self):
        return f"{self.ship_model} - {self.collection_time}"


class BoatTrackRecord(models.Model):
    """船体轨迹记录（用于地图轨迹回放）"""

    ship_model = models.CharField(max_length=50, db_index=True, help_text='船型号')
    ship_port = models.IntegerField(null=True, blank=True, db_index=True, help_text='来源端口')
    boat_timestamp = models.CharField(max_length=20, null=True, blank=True, help_text='设备时间原始值')
    device_time = models.DateTimeField(null=True, blank=True, db_index=True, help_text='设备时间')
    latitude = models.FloatField(help_text='纬度')
    longitude = models.FloatField(help_text='经度')
    course = models.FloatField(null=True, blank=True, help_text='航向(度)')
    speed = models.FloatField(null=True, blank=True, help_text='速度(米/秒)')
    battery_level = models.CharField(max_length=50, null=True, blank=True, help_text='电池电压')
    water_extraction = models.CharField(max_length=100, null=True, blank=True, help_text='采水样执行阶段')
    recorded_at = models.DateTimeField(auto_now_add=True, db_index=True, help_text='入库时间')

    class Meta:
        verbose_name = '船体轨迹记录'
        verbose_name_plural = '船体轨迹记录'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['ship_model', '-recorded_at']),
            models.Index(fields=['ship_port', '-recorded_at']),
        ]

    def __str__(self):
        return f"{self.ship_model} ({self.latitude}, {self.longitude}) @ {self.recorded_at}"


class VideoStreamTransferRecord(models.Model):
    """视频流传输记录（终端转发到服务端）"""

    ship_model = models.CharField(max_length=50, db_index=True, help_text='船型号')
    stream_protocol = models.CharField(max_length=30, default='RTSP', help_text='流协议，如RTSP')
    video_codec = models.CharField(max_length=30, default='H265', help_text='视频编码格式')
    transport_protocol = models.CharField(max_length=20, default='UDP', help_text='传输协议，如UDP/TCP')
    source_ip = models.CharField(max_length=64, blank=True, default='', help_text='源IP')
    source_port = models.IntegerField(null=True, blank=True, help_text='源端口')
    target_ip = models.CharField(max_length=64, blank=True, default='', help_text='目标IP')
    target_port = models.IntegerField(null=True, blank=True, help_text='目标端口')
    stream_url = models.CharField(max_length=500, blank=True, default='', help_text='视频流地址')

    frame_width = models.IntegerField(null=True, blank=True, help_text='视频宽度')
    frame_height = models.IntegerField(null=True, blank=True, help_text='视频高度')
    fps = models.FloatField(null=True, blank=True, help_text='帧率')
    bitrate_kbps = models.FloatField(null=True, blank=True, help_text='码率(kbps)')
    packet_size = models.IntegerField(null=True, blank=True, help_text='每包字节数')
    packet_count = models.BigIntegerField(default=0, help_text='累计传输包数')
    frame_count = models.BigIntegerField(default=0, help_text='累计传输帧数')
    loss_rate = models.FloatField(default=0, help_text='丢包率(%)')
    latency_ms = models.FloatField(null=True, blank=True, help_text='延迟(ms)')
    jitter_ms = models.FloatField(null=True, blank=True, help_text='抖动(ms)')

    status = models.CharField(max_length=20, default='normal', help_text='传输状态')
    warn = models.CharField(max_length=50, default='0', help_text='警告码，默认0')
    timestamp = models.DateTimeField(null=True, blank=True, db_index=True, help_text='设备上传时间')
    collection_time = models.DateTimeField(auto_now_add=True, db_index=True, help_text='入库时间')
    raw_payload = models.TextField(blank=True, default='', help_text='原始上报内容(可选)')

    class Meta:
        verbose_name = '视频流传输记录'
        verbose_name_plural = '视频流传输记录'
        ordering = ['-collection_time']
        indexes = [
            models.Index(fields=['ship_model', '-collection_time']),
            models.Index(fields=['-timestamp']),
        ]

    def __str__(self):
        return f"{self.ship_model} {self.video_codec}/{self.transport_protocol} @ {self.collection_time}"
