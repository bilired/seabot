from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_imagetransferrecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='address',
            field=models.CharField(blank=True, default='', help_text='地址', max_length=255),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='description',
            field=models.TextField(blank=True, default='', help_text='个人介绍'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(blank=True, default='', help_text='性别编码：1男 2女', max_length=2),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='nick_name',
            field=models.CharField(blank=True, default='', help_text='昵称', max_length=50),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='real_name',
            field=models.CharField(blank=True, default='', help_text='姓名', max_length=50),
        ),
    ]
