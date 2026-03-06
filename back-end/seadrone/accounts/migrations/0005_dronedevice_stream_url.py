from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_monthlysalesdata_usergrowthdata'),
    ]

    operations = [
        migrations.AddField(
            model_name='dronedevice',
            name='stream_url',
            field=models.CharField(blank=True, default='', help_text='直播拉流地址', max_length=500),
        ),
    ]
