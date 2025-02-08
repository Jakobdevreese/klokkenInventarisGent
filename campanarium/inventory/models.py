from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator

# Model for the inventory
# 
# Bell(id, name, inscription, year, pitch, weight, ornaments, function, manufacturer, carillon, location, location_comment, comments)
# Manifecturer(id, name, isCompany, adress, country, years_operations, comments)
# Tower(id, name, church, geo_coordinates, heigt, height_bells, comments, contacts)
# Carillon(id, name, established, number_of_bells, total_weight, comments, transposition)
# File(id, file, file_type, comments, bell_id, carillon_id, manifacturer_id, tower_id)

# Bell model
# Bell(id, name, inscription, year, pitch, weight, ornaments, function, manufacturer, carillon, location, location_comment, comments)
class Bell(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=100, verbose_name='Naam')
    inscription = models.CharField(max_length=255, verbose_name='Inscriptie', blank=True, null=True)
    year = models.IntegerField(
        verbose_name='Gietjaar',
        validators=[MinValueValidator(600), MaxValueValidator(2100)]
    )
    pitch = models.CharField(max_length=20, verbose_name='Slagtoon')
    weight = models.FloatField(
        verbose_name='Gewicht (kg)',
        validators=[MinValueValidator(0.0)]
    )
    ornaments = models.CharField(max_length=100, verbose_name='Versiering', blank=True, null=True)
    function = models.CharField(max_length=100, verbose_name='Functie')
    manufacturer = models.ForeignKey(
        'Manufacturer', 
        on_delete=models.CASCADE,
        verbose_name='Gieter'
    )
    carillon = models.ForeignKey(
        'Carillon', 
        on_delete=models.CASCADE,
        verbose_name='Beiaard'
    )
    location = models.ForeignKey(
        'Tower', 
        on_delete=models.CASCADE,
        verbose_name='Toren'
    )
    location_comment = models.CharField(max_length=255, verbose_name='Locatie Opmerking', blank=True, null=True)
    comments = models.TextField(verbose_name='Opmerkingen', blank=True, null=True)

    class Meta:
        verbose_name = 'Klok'
        verbose_name_plural = 'Klokken'
        ordening = ['year', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.year}) - {self.manufacturer.name} - {self.location.name}"

# Manufacturer model
# Manufacturer(id, name, isCompany, adress, country, years_operations, comments)
class Manufacturer(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=100, verbose_name='Naam')
    isCompany = models.BooleanField(verbose_name='Is een bedrijf')
    adress = models.CharField(max_length=255, verbose_name='Adres', blank=True, null=True)
    country = models.CharField(max_length=100, verbose_name='Land')
    years_operations = models.CharField(max_length=100, verbose_name='Jaren actief', blank=True, null=True)
    comments = models.TextField(verbose_name='Opmerkingen', blank=True, null=True)

    class Meta:
        verbose_name = 'Gieter'
        verbose_name_plural = 'Gieters'
        ordening = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.country}"

# Tower model
# Tower(id, name, church, geo_coordinates, heigt, height_bells, comments, contacts)
class Tower(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=100, verbose_name='Naam')
    church = models.CharField(max_length=100, verbose_name='Kerk')
    geo_coordinates = models.CharField(max_length=100, verbose_name='Geografische Coördinaten', blank=True, null=True)
    height = models.FloatField(
        verbose_name='Hoogte (m)',
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    height_bells = models.FloatField(
        verbose_name='Hoogte klokken (m)',
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    comments = models.TextField(verbose_name='Opmerkingen', blank=True, null=True)
    contacts = models.TextField(verbose_name='Contacten', blank=True, null=True)

    class Meta:
        verbose_name = 'Toren'
        verbose_name_plural = 'Torens'
        ordening = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.church}"

# Carillon model
# Carillon(id, name, established, number_of_bells, total_weight, comments, transposition)
class Carillon(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=100, verbose_name='Naam')
    established = models.IntegerField(
        verbose_name='Ingebruikname',
        validators=[MinValueValidator(600), MaxValueValidator(2100)]
    )
    number_of_bells = models.IntegerField(
        verbose_name='Aantal klokken',
        validators=[MinValueValidator(0), MaxValueValidator(80)]
    )
    total_weight = models.FloatField(
        verbose_name='Totaal gewicht (kg)',
        validators=[MinValueValidator(0.0), MaxValueValidator(100_000.0)]
    )
    comments = models.TextField(verbose_name='Opmerkingen', blank=True, null=True)
    transposition = models.CharField(max_length=20, verbose_name='Transpositie', blank=True, null=True)
    tower = models.ForeignKey(
        'Tower', 
        on_delete=models.CASCADE,
        verbose_name='Toren'
    )

    class Meta:
        verbose_name = 'Beiaard'
        verbose_name_plural = 'Beiaarden'
        ordening = ['weight', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.established} - {self.tower.name}"

# File model
# File(id, file, file_type, comments, bell_id, carillon_id, manifacturer_id, tower_id)
class File(models.Model):
    # Define allowed file types as choices
    FILE_TYPE_CHOICES = [
        ('image', 'Image (png, jpg, jpeg, svg, webp)'),
        ('pdf', 'PDF'),
        ('csv', 'CSV'),
    ]

    id = models.AutoField(primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=100, verbose_name='Naam')
    file = models.FileField(
        verbose_name='Bestand',
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'svg', 'webp', 'pdf', 'csv'])]
    )
    file_type = models.CharField(
        max_length=10, 
        choices=FILE_TYPE_CHOICES,
        verbose_name='Bestandstype'
    )
    comments = models.TextField(verbose_name='Opmerkingen', blank=True, null=True)
    bell = models.ForeignKey(
        'Bell', 
        on_delete=models.CASCADE,
        verbose_name='Klok'
    )
    carillon = models.ForeignKey(
        'Carillon', 
        on_delete=models.CASCADE,
        verbose_name='Beiaard'
    )
    manufacturer = models.ForeignKey(
        'Manufacturer', 
        on_delete=models.CASCADE,
        verbose_name='Gieter'
    )
    tower = models.ForeignKey(
        'Tower', 
        on_delete=models.CASCADE,
        verbose_name='Toren'
    )

    class Meta:
        verbose_name = 'Bestand'
        verbose_name_plural = 'Bestanden'
        ordening = ['name', 'file_type']
    
    def __str__(self):
        return f"{self.file_type} - {self.bell.name} - {self.carillon.name} - {self.manufacturer.name} - {self.tower.name}"
