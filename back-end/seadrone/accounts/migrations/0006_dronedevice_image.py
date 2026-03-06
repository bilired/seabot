from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_dronedevice_stream_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='dronedevice',
            name='image',
            field=models.CharField(blank=True, default='', help_text='设备照片URL', max_length=500),
        ),
    ]
