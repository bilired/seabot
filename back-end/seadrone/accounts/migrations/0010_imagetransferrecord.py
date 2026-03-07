from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_userprofile_mobile'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageTransferRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ship_model', models.CharField(default='未知型号', help_text='船型/设备型号', max_length=50)),
                ('image_uid', models.CharField(help_text='图片唯一标识', max_length=64, unique=True)),
                ('timestamp', models.DateTimeField(help_text='图片时间戳')),
                ('image_format', models.CharField(default='jpg', help_text='图片格式', max_length=16)),
                ('resolution', models.CharField(blank=True, default='', help_text='分辨率，例如1920x1080', max_length=32)),
                ('file_size_mb', models.FloatField(default=0, help_text='文件大小(MB)')),
                ('image_url', models.CharField(help_text='图片URL', max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                (
                    'owner',
                    models.ForeignKey(
                        blank=True,
                        help_text='记录归属用户',
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='image_transfer_records',
                        to='auth.user'
                    )
                ),
            ],
            options={
                'verbose_name': '图像传输记录',
                'verbose_name_plural': '图像传输记录',
                'ordering': ['-timestamp', '-id'],
            },
        ),
    ]
