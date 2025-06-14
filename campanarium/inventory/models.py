from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.contrib.gis.db import models as gis_models

# Model for the inventory
# 
# Bell(id, name, weight, height, diameter, inscription, pitch, installation, year, function, comments)
# Founder(id, primary_name, alternative_names, company_name, active_period, geographic_location, country, comments)
# Tower(id, name, building, geo_coordinates, adress, height, height_bells, comments, contact_info)
# Carillon(id, established, number_of_bells, total_weight, transposition, keyboard_standard, comments)
# File(id, file, file_type, bell_id, carillon_id, tower_id, manifacturer_id, comments, file_name)
#
# Relation tables
#
# Bell_Tower(id, bell_id, tower_id, isCurrentLocation, startDate, endDate, installationDetails, comments)
# Carillon_Bell(id, bell_id, carillon_id, startDate, endDate, comments, relativePitch)
# Bell_Founder(id, bell_id, founder_id, dateOfWork, typeOfWork, isPrimaryFounder, comments)
#

# Bell model
# Bell(id, name, weight, height, diameter, inscription, pitch, installation, year, function, comments)
class Bell(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=100, verbose_name='Naam')
    weight = models.FloatField(
        verbose_name='Gewicht (kg)',
        validators=[MinValueValidator(0.0)]
    )
    height = models.FloatField(
        verbose_name='Hoogte (cm)',
        validators=[MinValueValidator(0.0)]
    )
    diameter = models.FloatField(
        verbose_name='Diameter (cm)',
        validators=[MinValueValidator(0.0)]
    )
    inscription = models.CharField(max_length=255, verbose_name='Inscriptie', blank=True, null=True)
    pitch = models.CharField(max_length=20, verbose_name='Slagtoon')
    installation = models.CharField(max_length=255, verbose_name='Opstelling')
    year = models.IntegerField(
        verbose_name='Gietjaar',
        validators=[MinValueValidator(600), MaxValueValidator(2100)]
    )
    function = models.CharField(max_length=100, verbose_name='Functie')
    comments = models.TextField(verbose_name='Opmerkingen', blank=True, null=True)

    class Meta:
        verbose_name = 'Klok'
        verbose_name_plural = 'Klokken'
    
    def __str__(self):
        return f"{self.name} ({self.year})"

# Founder Model
# Founder(id, primary_name, alternative_names, company_name, active_period, geographic_location, country, comments)
class Founder(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    primary_name = models.CharField(max_length=100, verbose_name='Naam')
    alternative_names = models.JSONField(
        default=list, 
        blank=True, 
        verbose_name='Alternatieve namen',
        help_text='Lijst van alternatieve namen'
    )
    company_name = models.CharField(max_length=100, verbose_name='Bedrijfsnaam', blank=True, null=True)
    active_period = models.CharField(
        max_length=100, 
        verbose_name='Jaren actief', 
        blank=True, 
        null=True,
        help_text='Bijvoorbeeld: "1850-1900", "ca. 1860", "vroege 19e eeuw", "actief rond 1875"'
    )
    geographic_location = models.CharField(max_length=255, verbose_name='Regio', help_text='Bijvoorbeeld: "Vlaanderen", "Braband", "Nederland",...')
    country = models.CharField(max_length=255, verbose_name='Land', help_text='Land van oprichting')
    comments = models.TextField(verbose_name='Opmerkingen', blank=True, null=True)

    class Meta:
        verbose_name = 'Gieter'
        verbose_name_plural = 'Gieters'
        ordering = ['primary_name']
    
    def __str__(self):
        return f"{self.primary_name} - {self.country}"

# Tower model
# Tower(id, name, building, geo_coordinates, adress, height, height_bells, comments, contact_info)
class Tower(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=100, verbose_name='Naam')
    building = models.CharField(max_length=100, verbose_name='Kerk of naam gebouw')
    geo_coordinates = gis_models.PointField(
        verbose_name='Geografische Coördinaten',
        blank=True,
        null=True,
        help_text='Klik op de kaart of voer coördinaten in'
    )
    street_address = models.CharField(max_length=200, verbose_name='Straat en huisnummer', blank=True, null=True)
    postal_code = models.CharField(max_length=10, verbose_name='Postcode', blank=True, null=True)
    city = models.CharField(max_length=100, verbose_name='Stad/Gemeente', blank=True, null=True)
    country = models.CharField(max_length=100, verbose_name='Land', default='België')

    # Full address for display/search
    full_address = models.CharField(
        max_length=300, 
        verbose_name='Volledig adres', 
        blank=True, 
        null=True,
        help_text='Automatisch gegenereerd of handmatig ingevoerd'
    )

    height = models.FloatField(
        verbose_name='Hoogte (m)',
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    height_bells = models.FloatField(
        verbose_name='Hoogte klokken (m)',
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    comments = models.TextField(verbose_name='Opmerkingen', blank=True, null=True)
    contact_info = models.TextField(verbose_name='Contacten', blank=True, null=True)

    class Meta:
        verbose_name = 'Toren'
        verbose_name_plural = 'Torens'
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        # Auto-generate full_address if structured fields are provided
        if self.street_address or self.city:
            parts = [self.street_address, f"{self.postal_code} {self.city}".strip(), self.country]
            self.full_address = ", ".join([part for part in parts if part])
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.building}"


# Carillon model
# Carillon(id, established, number_of_bells, total_weight, transposition, keyboard_standard, comments)
class Carillon(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    tower = models.ForeignKey(
        'Tower', 
        on_delete=models.CASCADE,
        verbose_name='Toren'
    )
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
    transposition = models.CharField(max_length=20, verbose_name='Transpositie', blank=True, null=True)
    keyboard_standard = models.CharField(max_length=20, verbose_name='Toetsenbord standaard', blank=True, null=True)
    comments = models.TextField(verbose_name='Opmerkingen', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Beiaard'
        verbose_name_plural = 'Beiaarden'
        ordering = ['tower__name', 'established']
    
    def __str__(self):
        return f"{self.tower.name} - {self.established}"


# File model
# File(id, file, file_type, bell_id, carillon_id, tower_id, manifacturer_id, comments, file_name)
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
        verbose_name='Klok',
        blank=True,
        null=True
    )
    carillon = models.ForeignKey(
        'Carillon', 
        on_delete=models.CASCADE,
        verbose_name='Beiaard',
        blank=True,
        null=True
    )
    founder = models.ForeignKey(
        'Manufacturer', 
        on_delete=models.CASCADE,
        verbose_name='Gieter',
        blank=True,
        null=True
    )
    tower = models.ForeignKey(
        'Tower', 
        on_delete=models.CASCADE,
        verbose_name='Toren',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Bestand'
        verbose_name_plural = 'Bestanden'
        ordering = ['name', 'file_type']
    
    def __str__(self):
        related_items = [item for item in [
            self.bell.name if self.bell else None,
            self.tower.name if self.tower else None,
            self.founder.primary_name if self.founder else None
        ] if item]
        return f"{self.name} ({self.file_type}) - {', '.join(related_items) if related_items else 'No relations'}"


# Bell_Tower(id, bell_id, tower_id, isCurrentLocation, startDate, endDate, installationDetails, comments)
class Bell_Tower(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    tower = models.ForeignKey(Tower, on_delete=models.CASCADE)
    bell = models.ForeignKey(Bell, on_delete=models.CASCADE)
    isCurrentLocation = models.BooleanField(verbose_name='Huidige locatie', default=False)
    start_date = models.DateField(  # Snake_case naming
        verbose_name='Startdatum', 
        blank=True, 
        null=True
    )
    end_date = models.DateField(  # Snake_case naming
        verbose_name='Einddatum', 
        blank=True, 
        null=True
    )
    is_current_location = models.BooleanField(  # Snake_case naming
        verbose_name='Huidige locatie', 
        default=False
    )
    installation_details = models.TextField(  # Snake_case naming
        verbose_name='Installatie details', 
        blank=True, 
        null=True
    )
    reason_of_movement = models.TextField(  # Snake_case naming
        verbose_name='Reden van verplaatsing', 
        blank=True, 
        null=True
    )
    comments = models.TextField(verbose_name='Opmerkingen', blank=True, null=True)
    
    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError('Startdatum kan niet na einddatum zijn')

    class Meta:
        unique_together = ('tower', 'bell')
        verbose_name = 'Toren Klok'
        verbose_name_plural = 'Torens Klokken'
    
    def __str__(self):
        return f"{self.tower.name} - {self.bell.name}"


# Carillon_Bell(id, bell_id, carillon_id, startDate, endDate, comments, relativePitch)
class Carillon_Bell(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    carillon = models.ForeignKey(Carillon, on_delete=models.CASCADE)
    bell = models.ForeignKey(Bell, on_delete=models.CASCADE)
    startDate = models.DateField(verbose_name='Startdatum', blank=True, null=True)
    endDate = models.DateField(verbose_name='Einddatum', blank=True, null=True)
    relativePitch = models.CharField(max_length=25, blank=True, null=True)
    comments = models.TextField(verbose_name='Opmerkingen', blank=True, null=True)

    class Meta:
        unique_together = ('carillon', 'bell')
        verbose_name = 'Beiaard Klok'
        verbose_name_plural = 'Beiaarden Klokken'
    
    def __str__(self):
        return f"{self.carillon.name} - {self.bell.name}"


# Bell_Founder(id, bell_id, founder_id, dateOfWork, typeOfWork, isPrimaryFounder, comments)
class Bell_Founder(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    bell = models.ForeignKey(Bell, on_delete=models.CASCADE)
    founder = models.ForeignKey(Founder, on_delete=models.CASCADE)
    date_of_work = models.IntegerField(  # Changed to year instead of date
        verbose_name='Jaar van werken',
        blank=True,
        null=True,
        validators=[MinValueValidator(600), MaxValueValidator(2100)],
        help_text='Jaar waarin het werk werd uitgevoerd'
    )
    type_of_work = models.CharField(  # Snake_case naming
        max_length=100, 
        verbose_name='Type van werken', 
        blank=True, 
        null=True,
        help_text='Bijvoorbeeld: "gieten", "reparatie", "hergieten"'
    )
    is_primary_founder = models.BooleanField(  # Snake_case naming
        verbose_name='Is primaire gieter', 
        default=False
    )
    comments = models.TextField(verbose_name='Opmerkingen', blank=True, null=True)

    class Meta:
        unique_together = ('bell', 'founder')
        verbose_name = 'Klok Gieter'
        verbose_name_plural = 'Klokken Gieters'
    
    def __str__(self):
        return f"{self.bell.name} - {self.founder.name}"
