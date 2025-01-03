# Generated by Django 5.0.1 on 2024-12-23 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0013_edi834data_group_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='EDI_USER_DATA',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_name', models.CharField(max_length=100)),
                ('first_name', models.CharField(max_length=100)),
                ('ssn', models.CharField(max_length=11, unique=True)),
                ('sub_dep', models.CharField(max_length=50)),
                ('status', models.CharField(max_length=50)),
                ('type', models.CharField(max_length=50)),
                ('phone', models.CharField(blank=True, max_length=15, null=True)),
                ('address1', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('zip', models.CharField(max_length=10)),
                ('dob', models.DateField()),
                ('sex', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], max_length=1)),
                ('plan', models.CharField(blank=True, max_length=100, null=True)),
                ('class_field', models.CharField(blank=True, max_length=100, null=True)),
                ('eff_date', models.DateField()),
                ('id_field', models.CharField(max_length=100, unique=True)),
                ('dep_first_name', models.CharField(blank=True, max_length=100, null=True)),
                ('dep_last_name', models.CharField(blank=True, max_length=100, null=True)),
                ('dep_dob', models.DateField(blank=True, null=True)),
                ('dep_ssn', models.CharField(blank=True, max_length=11, null=True)),
                ('dep_sex', models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female')], max_length=1, null=True)),
                ('code', models.CharField(max_length=100, null=True)),
                ('definition', models.TextField(blank=True, null=True)),
                ('custodial_address1', models.CharField(blank=True, max_length=255, null=True)),
                ('custodial_city', models.CharField(blank=True, max_length=100, null=True)),
                ('custodial_state', models.CharField(blank=True, max_length=100, null=True)),
                ('custodial_zip', models.CharField(blank=True, max_length=10, null=True)),
                ('custodial_phone', models.CharField(blank=True, max_length=15, null=True)),
                ('address2', models.CharField(blank=True, max_length=255, null=True)),
                ('date_edi', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
    ]
