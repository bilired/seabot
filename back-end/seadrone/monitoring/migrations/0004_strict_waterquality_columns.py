from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0003_align_waterquality_doc_fields'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql='ALTER TABLE monitoring_waterqualitydata RENAME COLUMN ph TO pH;',
                    reverse_sql='ALTER TABLE monitoring_waterqualitydata RENAME COLUMN pH TO ph;',
                ),
                migrations.RunSQL(
                    sql='ALTER TABLE monitoring_waterqualitydata RENAME COLUMN algae TO blue_green;',
                    reverse_sql='ALTER TABLE monitoring_waterqualitydata RENAME COLUMN blue_green TO algae;',
                ),
                migrations.RunSQL(
                    sql='ALTER TABLE monitoring_waterqualitydata RENAME COLUMN warning_code TO warn;',
                    reverse_sql='ALTER TABLE monitoring_waterqualitydata RENAME COLUMN warn TO warning_code;',
                ),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name='waterqualitydata',
                    name='pH',
                    field=models.FloatField(help_text='pH值'),
                ),
                migrations.AlterField(
                    model_name='waterqualitydata',
                    name='blue_green',
                    field=models.FloatField(help_text='蓝绿藻(cells/mL)'),
                ),
                migrations.AlterField(
                    model_name='waterqualitydata',
                    name='warn',
                    field=models.CharField(default='0', help_text='警告码，默认0', max_length=50),
                ),
            ],
        ),
    ]
