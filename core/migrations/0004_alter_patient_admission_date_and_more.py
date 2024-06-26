# Generated by Django 5.0.2 on 2024-04-11 03:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_rename_full_name_patient_fullname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='admission_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='patient',
            name='condition_type',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='patient',
            name='severity',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='patient',
            name='status',
            field=models.CharField(max_length=255, null=True),
        ),
    ]