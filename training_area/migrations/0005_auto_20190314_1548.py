# Generated by Django 2.1.7 on 2019-03-14 07:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('training_area', '0004_auto_20190314_1547'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='coach',
        ),
        migrations.AlterField(
            model_name='event',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_calendar', to=settings.AUTH_USER_MODEL),
        ),
    ]