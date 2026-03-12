from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0005_align_boattrackrecord_doc_fields'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql='ALTER TABLE monitoring_nutrientdata ADD COLUMN timestamp datetime NULL;',
                    reverse_sql='ALTER TABLE monitoring_nutrientdata DROP COLUMN timestamp;',
                ),
                migrations.RunSQL(
                    sql='UPDATE monitoring_nutrientdata SET timestamp = collection_time WHERE timestamp IS NULL;',
                    reverse_sql=migrations.RunSQL.noop,
                ),
                migrations.RunSQL(
                    sql='ALTER TABLE monitoring_nutrientdata ADD COLUMN status integer NOT NULL DEFAULT 0;',
                    reverse_sql='ALTER TABLE monitoring_nutrientdata DROP COLUMN status;',
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE monitoring_nutrientdata ADD COLUMN warn varchar(50) NOT NULL DEFAULT '0';",
                    reverse_sql='ALTER TABLE monitoring_nutrientdata DROP COLUMN warn;',
                ),
                migrations.RunSQL(
                    sql="UPDATE monitoring_nutrientdata SET warn = COALESCE(error_code1, '0');",
                    reverse_sql=migrations.RunSQL.noop,
                ),
                migrations.RunSQL(
                    sql='ALTER TABLE monitoring_nutrientdata RENAME COLUMN phosphate TO phosphates;',
                    reverse_sql='ALTER TABLE monitoring_nutrientdata RENAME COLUMN phosphates TO phosphate;',
                ),
                migrations.RunSQL(
                    sql='ALTER TABLE monitoring_nutrientdata RENAME COLUMN phosphate_time TO phosphates_timestamp;',
                    reverse_sql='ALTER TABLE monitoring_nutrientdata RENAME COLUMN phosphates_timestamp TO phosphate_time;',
                ),
                migrations.RunSQL(
                    sql='ALTER TABLE monitoring_nutrientdata RENAME COLUMN ammonia TO ammonia_nitrogen;',
                    reverse_sql='ALTER TABLE monitoring_nutrientdata RENAME COLUMN ammonia_nitrogen TO ammonia;',
                ),
                migrations.RunSQL(
                    sql='ALTER TABLE monitoring_nutrientdata RENAME COLUMN ammonia_time TO ammonia_nitrogen_timestamp;',
                    reverse_sql='ALTER TABLE monitoring_nutrientdata RENAME COLUMN ammonia_nitrogen_timestamp TO ammonia_time;',
                ),
                migrations.RunSQL(
                    sql='ALTER TABLE monitoring_nutrientdata RENAME COLUMN nitrate_time TO nitrate_timestamp;',
                    reverse_sql='ALTER TABLE monitoring_nutrientdata RENAME COLUMN nitrate_timestamp TO nitrate_time;',
                ),
                migrations.RunSQL(
                    sql='ALTER TABLE monitoring_nutrientdata RENAME COLUMN nitrite TO sub_nitrate;',
                    reverse_sql='ALTER TABLE monitoring_nutrientdata RENAME COLUMN sub_nitrate TO nitrite;',
                ),
                migrations.RunSQL(
                    sql='ALTER TABLE monitoring_nutrientdata RENAME COLUMN nitrite_time TO sub_nitrate_timestamp;',
                    reverse_sql='ALTER TABLE monitoring_nutrientdata RENAME COLUMN sub_nitrate_timestamp TO nitrite_time;',
                ),
                migrations.RunSQL(
                    sql='ALTER TABLE monitoring_nutrientdata DROP COLUMN error_code1;',
                    reverse_sql="ALTER TABLE monitoring_nutrientdata ADD COLUMN error_code1 varchar(10) NOT NULL DEFAULT '00';",
                ),
                migrations.RunSQL(
                    sql='ALTER TABLE monitoring_nutrientdata DROP COLUMN error_code2;',
                    reverse_sql="ALTER TABLE monitoring_nutrientdata ADD COLUMN error_code2 varchar(10) NOT NULL DEFAULT '00';",
                ),
                migrations.RunSQL(
                    sql='ALTER TABLE monitoring_nutrientdata DROP COLUMN instrument_status;',
                    reverse_sql="ALTER TABLE monitoring_nutrientdata ADD COLUMN instrument_status varchar(20) NOT NULL DEFAULT '正常';",
                ),
                migrations.RunSQL(
                    sql='ALTER TABLE monitoring_nutrientdata DROP COLUMN connection_status;',
                    reverse_sql="ALTER TABLE monitoring_nutrientdata ADD COLUMN connection_status varchar(20) NOT NULL DEFAULT '在线';",
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='nutrientdata',
                    name='timestamp',
                    field=models.DateTimeField(blank=True, db_index=True, help_text='时间戳', null=True),
                ),
                migrations.AddField(
                    model_name='nutrientdata',
                    name='status',
                    field=models.IntegerField(default=0, help_text='0未连接，1已连接'),
                ),
                migrations.AddField(
                    model_name='nutrientdata',
                    name='warn',
                    field=models.CharField(default='0', help_text='警告码，默认0', max_length=50),
                ),
                migrations.RenameField(
                    model_name='nutrientdata',
                    old_name='phosphate',
                    new_name='phosphates',
                ),
                migrations.RenameField(
                    model_name='nutrientdata',
                    old_name='phosphate_time',
                    new_name='phosphates_timestamp',
                ),
                migrations.RenameField(
                    model_name='nutrientdata',
                    old_name='ammonia',
                    new_name='ammonia_nitrogen',
                ),
                migrations.RenameField(
                    model_name='nutrientdata',
                    old_name='ammonia_time',
                    new_name='ammonia_nitrogen_timestamp',
                ),
                migrations.RenameField(
                    model_name='nutrientdata',
                    old_name='nitrate_time',
                    new_name='nitrate_timestamp',
                ),
                migrations.RenameField(
                    model_name='nutrientdata',
                    old_name='nitrite',
                    new_name='sub_nitrate',
                ),
                migrations.RenameField(
                    model_name='nutrientdata',
                    old_name='nitrite_time',
                    new_name='sub_nitrate_timestamp',
                ),
                migrations.RemoveField(
                    model_name='nutrientdata',
                    name='error_code1',
                ),
                migrations.RemoveField(
                    model_name='nutrientdata',
                    name='error_code2',
                ),
                migrations.RemoveField(
                    model_name='nutrientdata',
                    name='instrument_status',
                ),
                migrations.RemoveField(
                    model_name='nutrientdata',
                    name='connection_status',
                ),
                migrations.AlterField(
                    model_name='nutrientdata',
                    name='ship_model',
                    field=models.CharField(help_text='数据唯一标识(data_id)', max_length=50),
                ),
                migrations.AlterField(
                    model_name='nutrientdata',
                    name='ammonia_nitrogen',
                    field=models.FloatField(help_text='氨氮(mg/L)'),
                ),
                migrations.AlterField(
                    model_name='nutrientdata',
                    name='sub_nitrate',
                    field=models.FloatField(help_text='亚硝酸盐(mg/L)'),
                ),
            ],
        ),
    ]
