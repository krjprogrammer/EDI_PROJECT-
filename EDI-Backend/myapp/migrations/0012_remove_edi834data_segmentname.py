# Generated by Django 5.0.1 on 2024-12-17 18:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0011_edi834data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='edi834data',
            name='SegmentName',
        ),
    ]
