# Generated by Django 5.1.6 on 2025-02-08 15:55

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Carillon',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Naam')),
                ('established', models.IntegerField(validators=[django.core.validators.MinValueValidator(600), django.core.validators.MaxValueValidator(2100)], verbose_name='Ingebruikname')),
                ('number_of_bells', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(80)], verbose_name='Aantal klokken')),
                ('total_weight', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100000.0)], verbose_name='Totaal gewicht (kg)')),
                ('comments', models.TextField(blank=True, null=True, verbose_name='Opmerkingen')),
                ('transposition', models.CharField(blank=True, max_length=20, null=True, verbose_name='Transpositie')),
            ],
            options={
                'verbose_name': 'Beiaard',
                'verbose_name_plural': 'Beiaarden',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Naam')),
                ('isCompany', models.BooleanField(verbose_name='Is een bedrijf')),
                ('adress', models.CharField(blank=True, max_length=255, null=True, verbose_name='Adres')),
                ('country', models.CharField(max_length=100, verbose_name='Land')),
                ('years_operations', models.CharField(blank=True, max_length=100, null=True, verbose_name='Jaren actief')),
                ('comments', models.TextField(blank=True, null=True, verbose_name='Opmerkingen')),
            ],
            options={
                'verbose_name': 'Gieter',
                'verbose_name_plural': 'Gieters',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Tower',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Naam')),
                ('church', models.CharField(max_length=100, verbose_name='Kerk')),
                ('geo_coordinates', models.CharField(blank=True, max_length=100, null=True, verbose_name='Geografische Coördinaten')),
                ('height', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)], verbose_name='Hoogte (m)')),
                ('height_bells', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)], verbose_name='Hoogte klokken (m)')),
                ('comments', models.TextField(blank=True, null=True, verbose_name='Opmerkingen')),
                ('contacts', models.TextField(blank=True, null=True, verbose_name='Contacten')),
            ],
            options={
                'verbose_name': 'Toren',
                'verbose_name_plural': 'Torens',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Bell',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Naam')),
                ('inscription', models.CharField(blank=True, max_length=255, null=True, verbose_name='Inscriptie')),
                ('year', models.IntegerField(validators=[django.core.validators.MinValueValidator(600), django.core.validators.MaxValueValidator(2100)], verbose_name='Gietjaar')),
                ('pitch', models.CharField(max_length=20, verbose_name='Slagtoon')),
                ('weight', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Gewicht (kg)')),
                ('ornaments', models.CharField(blank=True, max_length=100, null=True, verbose_name='Versiering')),
                ('function', models.CharField(max_length=100, verbose_name='Functie')),
                ('location_comment', models.CharField(blank=True, max_length=255, null=True, verbose_name='Locatie Opmerking')),
                ('comments', models.TextField(blank=True, null=True, verbose_name='Opmerkingen')),
                ('carillon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.carillon', verbose_name='Beiaard')),
                ('manufacturer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.manufacturer', verbose_name='Gieter')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.tower', verbose_name='Toren')),
            ],
            options={
                'verbose_name': 'Klok',
                'verbose_name_plural': 'Klokken',
            },
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Naam')),
                ('file', models.FileField(upload_to='', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'svg', 'webp', 'pdf', 'csv'])], verbose_name='Bestand')),
                ('file_type', models.CharField(choices=[('image', 'Image (png, jpg, jpeg, svg, webp)'), ('pdf', 'PDF'), ('csv', 'CSV')], max_length=10, verbose_name='Bestandstype')),
                ('comments', models.TextField(blank=True, null=True, verbose_name='Opmerkingen')),
                ('bell', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.bell', verbose_name='Klok')),
                ('carillon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.carillon', verbose_name='Beiaard')),
                ('manufacturer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.manufacturer', verbose_name='Gieter')),
                ('tower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.tower', verbose_name='Toren')),
            ],
            options={
                'verbose_name': 'Bestand',
                'verbose_name_plural': 'Bestanden',
                'ordering': ['name', 'file_type'],
            },
        ),
        migrations.AddField(
            model_name='carillon',
            name='tower',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.tower', verbose_name='Toren'),
        ),
    ]
