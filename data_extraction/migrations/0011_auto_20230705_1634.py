# Generated by Django 3.2.8 on 2023-07-05 06:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data_extraction', '0010_auto_20230703_1106'),
    ]

    operations = [
        migrations.AddField(
            model_name='data',
            name='text10',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='data',
            name='text5',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='data',
            name='text6',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='data',
            name='text7',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='data',
            name='text8',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='data',
            name='text9',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='data',
            name='unit10',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='tenth_units', to='data_extraction.unit'),
        ),
        migrations.AddField(
            model_name='data',
            name='unit5',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='fifth_units', to='data_extraction.unit'),
        ),
        migrations.AddField(
            model_name='data',
            name='unit6',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='sixth_units', to='data_extraction.unit'),
        ),
        migrations.AddField(
            model_name='data',
            name='unit7',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='seventh_units', to='data_extraction.unit'),
        ),
        migrations.AddField(
            model_name='data',
            name='unit8',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='eigth_units', to='data_extraction.unit'),
        ),
        migrations.AddField(
            model_name='data',
            name='unit9',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='ninth_units', to='data_extraction.unit'),
        ),
        migrations.AddField(
            model_name='data',
            name='value10',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='data',
            name='value5',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='data',
            name='value6',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='data',
            name='value7',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='data',
            name='value8',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='data',
            name='value9',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='extractionaction',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Initial Action'), (1, 'Immediately Next Text'), (2, 'Find Text'), (3, 'Get Value'), (4, 'Get Text Value'), (6, 'Next Data Row'), (5, 'Save Data'), (11, 'Table Header'), (12, 'Table Row'), (13, 'Table Cell Value'), (14, 'Table Cell Text')]),
        ),
        migrations.AlterUniqueTogether(
            name='data',
            unique_together={('page', 'extraction_method', 'value', 'text', 'unit', 'value2', 'text2', 'unit2', 'value3', 'text3', 'unit3', 'value4', 'text4', 'unit4', 'value5', 'text5', 'unit5', 'value6', 'text6', 'unit6', 'value7', 'text7', 'unit7', 'value8', 'text8', 'unit8', 'value9', 'text9', 'unit9', 'value10', 'text10', 'unit10')},
        ),
    ]