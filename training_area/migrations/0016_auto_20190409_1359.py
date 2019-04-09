# Generated by Django 2.1.7 on 2019-04-09 05:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training_area', '0015_auto_20190409_1351'),
    ]

    operations = [
        migrations.AddField(
            model_name='accessory',
            name='is_complete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='accessory',
            name='load',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='accessory',
            name='load_done',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
