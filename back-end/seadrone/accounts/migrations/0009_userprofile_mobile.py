from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='mobile',
            field=models.CharField(blank=True, default='', help_text='手机号', max_length=20),
        ),
    ]
