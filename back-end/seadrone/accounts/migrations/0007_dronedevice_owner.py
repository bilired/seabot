from django.conf import settings
from django.db import migrations, models


def assign_existing_devices_to_first_user(apps, schema_editor):
    DroneDevice = apps.get_model('accounts', 'DroneDevice')
    User = apps.get_model('auth', 'User')

    first_user = User.objects.order_by('id').first()
    if first_user is None:
        return

    DroneDevice.objects.filter(owner__isnull=True).update(owner=first_user)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_dronedevice_image'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='dronedevice',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name='drone_devices', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RunPython(assign_existing_devices_to_first_user, migrations.RunPython.noop),
    ]
