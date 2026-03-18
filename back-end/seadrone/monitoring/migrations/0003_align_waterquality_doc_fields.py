from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0002_boattrackrecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='waterqualitydata',
            name='timestamp',
            field=models.DateTimeField(blank=True, db_index=True, help_text='时间戳', null=True),
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RenameField(
                    model_name='waterqualitydata',
                    old_name='ph',
                    new_name='pH',
                ),
                migrations.RenameField(
                    model_name='waterqualitydata',
                    old_name='algae',
                    new_name='blue_green',
                ),
                migrations.RenameField(
                    model_name='waterqualitydata',
                    old_name='warning_code',
                    new_name='warn',
                ),
                migrations.AlterField(
                    model_name='waterqualitydata',
                    name='pH',
                    field=models.FloatField(db_column='ph', help_text='pH值'),
                ),
                migrations.AlterField(
                    model_name='waterqualitydata',
                    name='blue_green',
                    field=models.FloatField(db_column='algae', help_text='蓝绿藻(cells/mL)'),
                ),
                migrations.AlterField(
                    model_name='waterqualitydata',
                    name='warn',
                    field=models.CharField(db_column='warning_code', default='0', help_text='警告码，默认0', max_length=50),
                ),
            ],
        ),
    ]
