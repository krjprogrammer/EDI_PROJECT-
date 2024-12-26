# Generated by Django 5.0.1 on 2024-12-17 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0010_dependent_eligibility_employee'),
    ]

    operations = [
        migrations.CreateModel(
            name='EDI834Data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('SegmentName', models.CharField(max_length=50)),
                ('ISA', models.CharField(blank=True, max_length=255, null=True)),
                ('GS', models.CharField(blank=True, max_length=255, null=True)),
                ('ST', models.CharField(blank=True, max_length=255, null=True)),
                ('BGN', models.CharField(blank=True, max_length=255, null=True)),
                ('DTP', models.CharField(blank=True, max_length=255, null=True)),
                ('N1', models.CharField(blank=True, max_length=255, null=True)),
                ('INS', models.CharField(blank=True, max_length=255, null=True)),
                ('REF', models.CharField(blank=True, max_length=255, null=True)),
                ('NM1', models.CharField(blank=True, max_length=255, null=True)),
                ('PER', models.CharField(blank=True, max_length=255, null=True)),
                ('N3', models.CharField(blank=True, max_length=255, null=True)),
                ('N4', models.CharField(blank=True, max_length=255, null=True)),
                ('DMG', models.CharField(blank=True, max_length=255, null=True)),
                ('HD', models.CharField(blank=True, max_length=255, null=True)),
                ('SE', models.CharField(blank=True, max_length=255, null=True)),
                ('GE', models.CharField(blank=True, max_length=255, null=True)),
                ('IEA', models.CharField(blank=True, max_length=255, null=True)),
                ('CreatedDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]