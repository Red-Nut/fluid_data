# Generated by Django 3.2.8 on 2023-06-14 01:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('company_name', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CompanyNameCorrections',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alternateName', models.CharField(max_length=255, unique=True)),
                ('correctName', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='DataType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('type_name', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('document_name', models.CharField(max_length=255)),
                ('url', models.TextField(max_length=1000, null=True)),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Missing'), (2, 'Downloaded'), (3, 'Ignored')], default=1)),
                ('converted', models.BooleanField(default=False, null=True)),
                ('conversion_status', models.PositiveSmallIntegerField(choices=[(1, 'Not Converted'), (2, 'Converted'), (3, 'Ignored')], default=1)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ExtractedDataTypes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('value1', models.CharField(max_length=100, null=True)),
                ('value2', models.CharField(max_length=100, null=True)),
                ('value3', models.CharField(max_length=100, null=True)),
                ('value4', models.CharField(max_length=100, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ExtractionAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('string', models.CharField(max_length=100, null=True)),
                ('type', models.PositiveSmallIntegerField(choices=[(0, 'Initial Action'), (1, 'Immediately Next Text'), (2, 'Find Text'), (3, 'Get Value'), (4, 'Get Text Value'), (6, 'Next Data Row'), (5, 'Save Data')])),
                ('direction', models.PositiveSmallIntegerField(choices=[(1, 'Left'), (2, 'Right'), (3, 'Up'), (4, 'Down')], null=True)),
                ('start', models.PositiveSmallIntegerField(null=True)),
                ('lower_bound', models.PositiveSmallIntegerField(choices=[(2, 'Start'), (1, 'Middle'), (0, 'Other End')], null=True)),
                ('lower_offset_percent', models.SmallIntegerField(null=True)),
                ('lower_offset_pixels', models.SmallIntegerField(null=True)),
                ('upper_bound', models.PositiveSmallIntegerField(choices=[(2, 'Start'), (1, 'Middle'), (0, 'Other End')], null=True)),
                ('upper_offset_percent', models.SmallIntegerField(null=True)),
                ('upper_offset_pixels', models.SmallIntegerField(null=True)),
                ('remove_chars', models.CharField(default=' #(#)#|', max_length=100, null=True)),
                ('can_fail', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('file_name', models.CharField(max_length=255)),
                ('file_ext', models.CharField(max_length=20)),
                ('file_location', models.TextField()),
                ('file_size', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('organisation_name', models.CharField(max_length=255)),
                ('api_key', models.CharField(max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('gov_id', models.CharField(max_length=100, unique=True)),
                ('modified', models.DateTimeField(blank=True, null=True)),
                ('checked', models.DateTimeField(auto_now=True)),
                ('success', models.BooleanField(default=False)),
                ('errorCodes', models.CharField(blank=True, max_length=100, null=True)),
                ('error', models.CharField(blank=True, max_length=1000, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('page_no', models.PositiveIntegerField()),
                ('extracted', models.BooleanField()),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pages', to='data_extraction.document')),
                ('file', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='data_extraction.file')),
            ],
            options={
                'unique_together': {('document_id', 'page_no')},
            },
        ),
        migrations.CreateModel(
            name='Permit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('permit_number', models.CharField(max_length=20)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ReportType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('type_name', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('name_long', models.CharField(max_length=50)),
                ('name_short', models.CharField(max_length=20)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=20)),
                ('metric_units', models.CharField(max_length=20)),
                ('metric_conversion', models.FloatField()),
                ('imperial_units', models.CharField(max_length=20)),
                ('imperial_conversion', models.FloatField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WellClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('class_name', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WellPurpose',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('purpose_name', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WellStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('status_name', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Well',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('gov_id', models.CharField(max_length=100, unique=True)),
                ('well_name', models.CharField(max_length=255, unique=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('rig_release', models.DateField(blank=True, null=True)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='data_extraction.company')),
                ('package', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='data_extraction.package')),
                ('permit', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='data_extraction.permit')),
                ('purpose', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='data_extraction.wellpurpose')),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='data_extraction.state')),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='data_extraction.wellstatus')),
                ('well_class', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='data_extraction.wellclass')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Active'), (2, 'Suspended'), (3, 'Requested'), (9, 'Deleted')], default=1)),
                ('privilege', models.PositiveSmallIntegerField(choices=[(0, 'Admin'), (1, 'Standard')], default=1)),
                ('metric_units', models.BooleanField(default=True)),
                ('organisation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_profiles', to='data_extraction.organisation')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserFileBucket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Requested'), (2, 'Preparing files'), (3, 'Ready to download'), (4, 'Archived')], default=1)),
                ('zipSize', models.PositiveIntegerField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Text',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='texts', to='data_extraction.page')),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('gov_id', models.CharField(max_length=100)),
                ('gov_report_name', models.CharField(max_length=255)),
                ('gov_creator', models.CharField(max_length=255)),
                ('gov_created', models.DateTimeField(blank=True, null=True)),
                ('gov_modified', models.DateTimeField(blank=True, null=True)),
                ('gov_dataset_completion_date', models.DateField(blank=True, null=True)),
                ('gov_open_file_date', models.DateField(blank=True, null=True)),
                ('report_name', models.CharField(max_length=255)),
                ('url', models.TextField(blank=True, max_length=1000, null=True)),
                ('report_owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='reports', to='data_extraction.company')),
                ('report_type', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='data_extraction.reporttype')),
                ('well', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='data_extraction.well')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OtherData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('gov_id', models.CharField(max_length=100)),
                ('gov_report_name', models.CharField(max_length=255)),
                ('gov_creator', models.CharField(max_length=255)),
                ('gov_created', models.DateTimeField(blank=True, null=True)),
                ('gov_modified', models.DateTimeField(blank=True, null=True)),
                ('gov_dataset_completion_date', models.DateField(blank=True, null=True)),
                ('gov_open_file_date', models.DateField(blank=True, null=True)),
                ('data_name', models.CharField(max_length=255)),
                ('url', models.TextField(blank=True, max_length=1000, null=True)),
                ('data_type', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='data_extraction.datatype')),
                ('package', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='data_extraction.package')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FileBucketFiles',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bucket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='data_extraction.userfilebucket')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_extraction.document')),
            ],
        ),
        migrations.CreateModel(
            name='ExtractionMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('company', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.RESTRICT, to='data_extraction.company')),
                ('data_type', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='data_extraction.extracteddatatypes')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ExtractionActions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('order', models.IntegerField()),
                ('action', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_extraction.extractionaction')),
                ('method', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actions', to='data_extraction.extractionmethod')),
            ],
            options={
                'ordering': ('order',),
            },
        ),
        migrations.AddField(
            model_name='extractionaction',
            name='unit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='data_extraction.unit'),
        ),
        migrations.AddField(
            model_name='document',
            name='file',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='data_extraction.file'),
        ),
        migrations.AddField(
            model_name='document',
            name='report',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='data_extraction.report'),
        ),
        migrations.AddField(
            model_name='document',
            name='well',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='data_extraction.well'),
        ),
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('text', models.CharField(max_length=100, null=True)),
                ('value2', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('text2', models.CharField(max_length=100, null=True)),
                ('value3', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('text3', models.CharField(max_length=100, null=True)),
                ('value4', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('text4', models.CharField(max_length=100, null=True)),
                ('extraction_method', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='datas', to='data_extraction.extractionmethod')),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='datas', to='data_extraction.page')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='data_extraction.unit')),
                ('unit2', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='second_units', to='data_extraction.unit')),
                ('unit3', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='third_units', to='data_extraction.unit')),
                ('unit4', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='forth_units', to='data_extraction.unit')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BoundingPoly',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.IntegerField()),
                ('y', models.IntegerField()),
                ('text', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='BoundingPolys', to='data_extraction.text')),
            ],
            options={
                'ordering': ('x', 'y'),
            },
        ),
    ]