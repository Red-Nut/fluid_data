# Generated by Django 3.2.8 on 2023-06-15 23:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_extraction', '0003_document_wellid_null'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='gov_id',
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
    ]