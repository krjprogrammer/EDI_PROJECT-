# Generated by Django 5.0.1 on 2024-12-25 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0018_edi_user_data_custodial_address2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='edi_user_data',
            name='code',
        ),
        migrations.RemoveField(
            model_name='edi_user_data',
            name='definition',
        ),
        migrations.AddField(
            model_name='edi_user_data',
            name='member_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
