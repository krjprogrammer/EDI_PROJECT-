# Generated by Django 5.0.1 on 2024-12-18 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0012_remove_edi834data_segmentname'),
    ]

    operations = [
        migrations.AddField(
            model_name='edi834data',
            name='group_id',
            field=models.IntegerField(default=0),
        ),
    ]
