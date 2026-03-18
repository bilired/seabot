from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0004_strict_waterquality_columns'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql='ALTER TABLE monitoring_boattrackrecord DROP COLUMN status;',
                    reverse_sql='ALTER TABLE monitoring_boattrackrecord ADD COLUMN status VARCHAR(50) NULL;',
                ),
                migrations.RunSQL(
                    sql='ALTER TABLE monitoring_boattrackrecord RENAME COLUMN direction TO course;',
                    reverse_sql='ALTER TABLE monitoring_boattrackrecord RENAME COLUMN course TO direction;',
                ),
                migrations.RunSQL(
                    sql='ALTER TABLE monitoring_boattrackrecord RENAME COLUMN battery_voltage TO battery_level;',
                    reverse_sql='ALTER TABLE monitoring_boattrackrecord RENAME COLUMN battery_level TO battery_voltage;',
                ),
                migrations.RunSQL(
                    sql='ALTER TABLE monitoring_boattrackrecord ADD COLUMN water_extraction VARCHAR(100) NULL;',
                    reverse_sql='ALTER TABLE monitoring_boattrackrecord DROP COLUMN water_extraction;',
                ),
            ],
            state_operations=[
                migrations.RemoveField(
                    model_name='boattrackrecord',
                    name='status',
                ),
                migrations.RenameField(
                    model_name='boattrackrecord',
                    old_name='direction',
                    new_name='course',
                ),
                migrations.RenameField(
                    model_name='boattrackrecord',
                    old_name='battery_voltage',
                    new_name='battery_level',
                ),
                migrations.AlterField(
                    model_name='boattrackrecord',
                    name='battery_level',
                    field=models.CharField(blank=True, help_text='电池电压', max_length=50, null=True),
                ),
                migrations.AlterField(
                    model_name='boattrackrecord',
                    name='speed',
                    field=models.FloatField(blank=True, help_text='速度(米/秒)', null=True),
                ),
                migrations.AddField(
                    model_name='boattrackrecord',
                    name='water_extraction',
                    field=models.CharField(blank=True, help_text='采水样执行阶段', max_length=100, null=True),
                ),
            ],
        ),
    ]
