from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0006_align_nutrient_doc_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoStreamTransferRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ship_model', models.CharField(db_index=True, help_text='船型号', max_length=50)),
                ('stream_protocol', models.CharField(default='RTSP', help_text='流协议，如RTSP', max_length=30)),
                ('video_codec', models.CharField(default='H265', help_text='视频编码格式', max_length=30)),
                ('transport_protocol', models.CharField(default='UDP', help_text='传输协议，如UDP/TCP', max_length=20)),
                ('source_ip', models.CharField(blank=True, default='', help_text='源IP', max_length=64)),
                ('source_port', models.IntegerField(blank=True, help_text='源端口', null=True)),
                ('target_ip', models.CharField(blank=True, default='', help_text='目标IP', max_length=64)),
                ('target_port', models.IntegerField(blank=True, help_text='目标端口', null=True)),
                ('stream_url', models.CharField(blank=True, default='', help_text='视频流地址', max_length=500)),
                ('frame_width', models.IntegerField(blank=True, help_text='视频宽度', null=True)),
                ('frame_height', models.IntegerField(blank=True, help_text='视频高度', null=True)),
                ('fps', models.FloatField(blank=True, help_text='帧率', null=True)),
                ('bitrate_kbps', models.FloatField(blank=True, help_text='码率(kbps)', null=True)),
                ('packet_size', models.IntegerField(blank=True, help_text='每包字节数', null=True)),
                ('packet_count', models.BigIntegerField(default=0, help_text='累计传输包数')),
                ('frame_count', models.BigIntegerField(default=0, help_text='累计传输帧数')),
                ('loss_rate', models.FloatField(default=0, help_text='丢包率(%)')),
                ('latency_ms', models.FloatField(blank=True, help_text='延迟(ms)', null=True)),
                ('jitter_ms', models.FloatField(blank=True, help_text='抖动(ms)', null=True)),
                ('status', models.CharField(default='normal', help_text='传输状态', max_length=20)),
                ('warn', models.CharField(default='0', help_text='警告码，默认0', max_length=50)),
                ('timestamp', models.DateTimeField(blank=True, db_index=True, help_text='设备上传时间', null=True)),
                ('collection_time', models.DateTimeField(auto_now_add=True, db_index=True, help_text='入库时间')),
                ('raw_payload', models.TextField(blank=True, default='', help_text='原始上报内容(可选)')),
            ],
            options={
                'verbose_name': '视频流传输记录',
                'verbose_name_plural': '视频流传输记录',
                'ordering': ['-collection_time'],
            },
        ),
        migrations.AddIndex(
            model_name='videostreamtransferrecord',
            index=models.Index(fields=['ship_model', '-collection_time'], name='monitoring_v_ship_mo_5f9a04_idx'),
        ),
        migrations.AddIndex(
            model_name='videostreamtransferrecord',
            index=models.Index(fields=['-timestamp'], name='monitoring_v_timesta_7d4fcc_idx'),
        ),
    ]
