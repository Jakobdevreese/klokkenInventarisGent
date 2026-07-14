from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.contrib.gis.db import models as gis_models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Model for the inventory
#
# Bell(id, name, weight, height, diameter, inscription, pitch, installation, year, function, ornaments, profile, comments)
# Founder(id, primary_name, alternative_names, company_name, active_period, geographic_location, country, comments)
# Tower(id, name, building, geo_coordinates, adress, height, height_bells, comments, contact_info)
# Carillon(id, tower, established, number_of_bells, total_weight, transposition, keyboard_standard, comments)
# File(id, file, file_type, bell_id, carillon_id, tower_id, founder_id, comments, name)
# BellPartial(id, bell, partial, frequency, note, cents_deviation, comments)
#
# Relation tables
#
# Bell_Tower(id, bell_id, tower_id, isCurrentLocation, startDate, endDate, installationDetails, comments)
# Carillon_Bell(id, bell_id, carillon_id, startDate, endDate, comments, relativePitch)
# Bell_Founder(id, bell_id, founder_id, dateOfWork, typeOfWork, isPrimaryFounder, comments)
#
# Feedback(id, content_object, subject, message, is_resolved) -- in-site tester feedback
#
# NOTE ON SEARCH: portable B-tree indexes are declared in each model's Meta for
# structured filtering (name, year, pitch, weight, ...). Free-text search is done
# in search_view() with a query-time PostgreSQL SearchVector ('dutch' config,
# name/inscription/comments), falling back to icontains on other backends. For
# larger datasets the next optimisation is a stored SearchVectorField kept in sync
# plus a GinIndex (Postgres-only, so it needs a vendor-guarded migration).


# ---------------------------------------------------------------------------
# Abstract base models
# ---------------------------------------------------------------------------

# Audit trail for a collaborative prototype: every record tracks when it was
# created/updated and by whom. Both timestamps use a static default (instead of
# auto_now/auto_now_add) so migrations stay non-interactive; updated_at is
# refreshed in save().
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Aangemaakt op')
    updated_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Bijgewerkt op')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True,
        verbose_name='Toegevoegd door'
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)


# Core domain entities additionally get a free-form JSON field so enthusiasts
# can record self-defined attributes without a schema migration. On PostgreSQL
# this is stored as JSONB and can be indexed with a GIN index for search.
class FlexibleModel(TimeStampedModel):
    custom_fields = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Extra velden',
        help_text='Vrije, zelf gedefinieerde eigenschappen als sleutel/waarde-paren'
    )

    class Meta:
        abstract = True


# ---------------------------------------------------------------------------
# Core entities
# ---------------------------------------------------------------------------

# Bell model
class Bell(FlexibleModel):
    FUNCTION_CHOICES = [
        ('luidklok', 'Luidklok'),
        ('uurklok', 'Uurklok'),
        ('beiaardklok', 'Beiaardklok'),
        ('gelui', 'Gelui'),
        ('andere', 'Andere'),
    ]

    id = models.AutoField(primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=100, verbose_name='Naam', blank=True, null=True)
    weight = models.FloatField(
        verbose_name='Gewicht (kg)',
        validators=[MinValueValidator(0.0)],
        blank=True,
        null=True
    )
    height = models.FloatField(
        verbose_name='Hoogte (cm)',
        validators=[MinValueValidator(0.0)],
        blank=True,
        null=True
    )
    diameter = models.FloatField(
        verbose_name='Diameter (cm)',
        validators=[MinValueValidator(0.0)],
        blank=True,
        null=True
    )
    inscription = models.CharField(max_length=255, verbose_name='Inscriptie', blank=True, null=True)
    pitch = models.CharField(max_length=20, verbose_name='Slagtoon', blank=True, null=True)
    installation = models.CharField(max_length=255, verbose_name='Opstelling', blank=True, null=True)
    year = models.IntegerField(
        verbose_name='Gietjaar',
        validators=[MinValueValidator(600), MaxValueValidator(2100)],
        blank=True,
        null=True
    )
    function = models.CharField(
        max_length=100,
        choices=FUNCTION_CHOICES,
        verbose_name='Functie',
        blank=True,
        null=True
    )
    ornaments = models.TextField(verbose_name='Versieringen', blank=True, null=True)
    profile = models.CharField(
        max_length=100,
        verbose_name='Profiel',
        blank=True,
        null=True,
        help_text='Bijvoorbeeld: zwaar, licht of medium profiel'
    )
    comments = models.TextField(verbose_name='Opmerkingen', blank=True, null=True)

    class Meta:
        verbose_name = 'Klok'
        verbose_name_plural = 'Klokken'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['year']),
            models.Index(fields=['pitch']),
            models.Index(fields=['weight']),
            models.Index(fields=['function']),
        ]

    def __str__(self):
        return f"{self.name} ({self.year})"

    def get_absolute_url(self):
        return reverse('bell_detail', kwargs={'pk': self.pk})


# Founder Model
class Founder(FlexibleModel):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    primary_name = models.CharField(max_length=100, verbose_name='Naam', blank=True, null=True)
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
    geographic_location = models.CharField(max_length=255, verbose_name='Regio', help_text='Bijvoorbeeld: "Vlaanderen", "Braband", "Nederland",...', blank=True, null=True)
    country = models.CharField(max_length=255, verbose_name='Land', help_text='Land van oprichting', blank=True, null=True)
    comments = models.TextField(verbose_name='Opmerkingen', blank=True, null=True)

    class Meta:
        verbose_name = 'Gieter'
        verbose_name_plural = 'Gieters'
        ordering = ['primary_name']
        indexes = [
            models.Index(fields=['primary_name']),
            models.Index(fields=['country']),
        ]

    def __str__(self):
        return f"{self.primary_name} - {self.country}"

    def get_absolute_url(self):
        return reverse('manufacturer_detail', kwargs={'pk': self.pk})


# Tower model
class Tower(FlexibleModel):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=100, verbose_name='Naam', blank=True, null=True)
    building = models.CharField(max_length=100, verbose_name='Kerk of naam gebouw', blank=True, null=True)
    geo_coordinates = gis_models.PointField(
        verbose_name='Geografische Coördinaten',
        blank=True,
        null=True,
        help_text='Klik op de kaart of voer coördinaten in'
    )
    street_address = models.CharField(max_length=200, verbose_name='Straat en huisnummer', blank=True, null=True)
    postal_code = models.CharField(max_length=10, verbose_name='Postcode', blank=True, null=True)
    city = models.CharField(max_length=100, verbose_name='Stad/Gemeente', blank=True, null=True)
    country = models.CharField(max_length=100, verbose_name='Land', default='België', blank=True, null=True)

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
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        blank=True,
        null=True
    )
    height_bells = models.FloatField(
        verbose_name='Hoogte klokken (m)',
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        blank=True,
        null=True
    )
    comments = models.TextField(verbose_name='Opmerkingen', blank=True, null=True)
    contact_info = models.TextField(verbose_name='Contacten', blank=True, null=True)

    class Meta:
        verbose_name = 'Toren'
        verbose_name_plural = 'Torens'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['city']),
        ]

    def save(self, *args, **kwargs):
        # Auto-generate full_address if structured fields are provided
        if self.street_address or self.city:
            parts = [self.street_address, f"{self.postal_code} {self.city}".strip(), self.country]
            self.full_address = ", ".join([part for part in parts if part])
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.building}"

    def get_absolute_url(self):
        return reverse('tower_detail', kwargs={'pk': self.pk})


# Carillon model
class Carillon(FlexibleModel):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    tower = models.ForeignKey(
        'Tower',
        on_delete=models.CASCADE,
        related_name='carillons',
        verbose_name='Toren'
    )
    established = models.IntegerField(
        verbose_name='Ingebruikname',
        validators=[MinValueValidator(600), MaxValueValidator(2100)],
        blank=True,
        null=True
    )
    number_of_bells = models.IntegerField(
        verbose_name='Aantal klokken',
        validators=[MinValueValidator(0), MaxValueValidator(80)],
        blank=True,
        null=True
    )
    total_weight = models.FloatField(
        verbose_name='Totaal gewicht (kg)',
        validators=[MinValueValidator(0.0), MaxValueValidator(100_000.0)],
        blank=True,
        null=True
    )
    transposition = models.CharField(max_length=20, verbose_name='Transpositie', blank=True, null=True)
    keyboard_standard = models.CharField(max_length=20, verbose_name='Toetsenbord standaard', blank=True, null=True)
    comments = models.TextField(verbose_name='Opmerkingen', blank=True, null=True)

    class Meta:
        verbose_name = 'Beiaard'
        verbose_name_plural = 'Beiaarden'
        ordering = ['tower__name', 'established']
        indexes = [
            models.Index(fields=['established']),
        ]

    def __str__(self):
        return f"{self.tower.name} - {self.established}"

    def get_absolute_url(self):
        return reverse('carillon_detail', kwargs={'pk': self.pk})


# BellPartial model -- the acoustic profile of a bell (campanometry). A bell has
# several partials (hum, prime, tierce, quint, nominal, ...); one row per partial
# keeps this structured yet open-ended.
class BellPartial(TimeStampedModel):
    PARTIAL_CHOICES = [
        ('hum', 'Zoemtoon (Hum)'),
        ('prime', 'Grondtoon (Prime)'),
        ('tierce', 'Terts (Tierce)'),
        ('quint', 'Kwint (Quint)'),
        ('nominal', 'Nominaal (Nominal)'),
        ('superquint', 'Superkwint (Superquint)'),
        ('octave_nominal', 'Octaafnominaal'),
        ('andere', 'Andere'),
    ]

    id = models.AutoField(primary_key=True, verbose_name='ID')
    bell = models.ForeignKey(Bell, on_delete=models.CASCADE, related_name='partials', verbose_name='Klok')
    partial = models.CharField(max_length=20, choices=PARTIAL_CHOICES, verbose_name='Boventoon')
    frequency = models.FloatField(
        verbose_name='Frequentie (Hz)',
        validators=[MinValueValidator(0.0)],
        blank=True,
        null=True
    )
    note = models.CharField(max_length=20, verbose_name='Noot', blank=True, null=True)
    cents_deviation = models.FloatField(verbose_name='Afwijking (cents)', blank=True, null=True)
    comments = models.TextField(verbose_name='Opmerkingen', blank=True, null=True)

    class Meta:
        verbose_name = 'Boventoon'
        verbose_name_plural = 'Boventonen'
        ordering = ['bell', 'frequency']

    def __str__(self):
        return f"{self.bell.name} - {self.get_partial_display()} ({self.frequency} Hz)"


# ---------------------------------------------------------------------------
# Files
# ---------------------------------------------------------------------------

def file_upload_path(instance, filename):
    # Organise uploads by type instead of dumping everything in MEDIA_ROOT.
    subdir = instance.file_type or 'overig'
    return f"uploads/{subdir}/{filename}"


# File model
class File(TimeStampedModel):
    # Define allowed file types as choices
    FILE_TYPE_CHOICES = [
        ('image', 'Image (png, jpg, jpeg, svg, webp)'),
        ('pdf', 'PDF'),
        ('csv', 'CSV'),
    ]

    # Map a file extension to its high-level type so file_type can be derived.
    EXTENSION_TO_TYPE = {
        'png': 'image', 'jpg': 'image', 'jpeg': 'image', 'svg': 'image', 'webp': 'image',
        'pdf': 'pdf',
        'csv': 'csv',
    }

    id = models.AutoField(primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=100, verbose_name='Naam')
    file = models.FileField(
        upload_to=file_upload_path,
        verbose_name='Bestand',
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'svg', 'webp', 'pdf', 'csv'])]
    )
    file_type = models.CharField(
        max_length=10,
        choices=FILE_TYPE_CHOICES,
        verbose_name='Bestandstype',
        blank=True,
        help_text='Automatisch afgeleid uit het bestand indien leeg gelaten'
    )
    comments = models.TextField(verbose_name='Opmerkingen', blank=True, null=True)
    bell = models.ForeignKey(
        'Bell',
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name='Klok',
        blank=True,
        null=True
    )
    carillon = models.ForeignKey(
        'Carillon',
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name='Beiaard',
        blank=True,
        null=True
    )
    founder = models.ForeignKey(
        'Founder',
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name='Gieter',
        blank=True,
        null=True
    )
    tower = models.ForeignKey(
        'Tower',
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name='Toren',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Bestand'
        verbose_name_plural = 'Bestanden'
        ordering = ['name', 'file_type']

    def save(self, *args, **kwargs):
        # Derive file_type from the extension when it was not set explicitly.
        if not self.file_type and self.file and '.' in self.file.name:
            ext = self.file.name.rsplit('.', 1)[-1].lower()
            self.file_type = self.EXTENSION_TO_TYPE.get(ext, '')
        super().save(*args, **kwargs)

    def __str__(self):
        related_items = [item for item in [
            self.bell.name if self.bell else None,
            self.carillon.tower.name if self.carillon else None,
            self.tower.name if self.tower else None,
            self.founder.primary_name if self.founder else None
        ] if item]
        return f"{self.name} ({self.file_type}) - {', '.join(related_items) if related_items else 'Geen relaties'}"


# ---------------------------------------------------------------------------
# Relation (junction) tables -- carry their own attributes, so they are modelled
# explicitly rather than as ManyToManyField. UniqueConstraints include the
# temporal/type field so a bell's history in a tower/carillon (and repeated work
# by the same founder) can be recorded.
# ---------------------------------------------------------------------------

class Bell_Tower(TimeStampedModel):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    tower = models.ForeignKey(Tower, on_delete=models.CASCADE, related_name='bell_links')
    bell = models.ForeignKey(Bell, on_delete=models.CASCADE, related_name='tower_links')
    start_date = models.DateField(
        verbose_name='Startdatum',
        blank=True,
        null=True
    )
    end_date = models.DateField(
        verbose_name='Einddatum',
        blank=True,
        null=True
    )
    is_current_location = models.BooleanField(
        verbose_name='Huidige locatie',
        default=False
    )
    installation_details = models.TextField(
        verbose_name='Installatie details',
        blank=True,
        null=True
    )
    reason_of_movement = models.TextField(
        verbose_name='Reden van verplaatsing',
        blank=True,
        null=True
    )
    comments = models.TextField(verbose_name='Opmerkingen', blank=True, null=True)

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError('Startdatum kan niet na einddatum zijn')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['tower', 'bell', 'start_date'], name='uniq_bell_tower_period')
        ]
        verbose_name = 'Toren Klok'
        verbose_name_plural = 'Torens Klokken'

    def __str__(self):
        return f"{self.tower.name} - {self.bell.name}"


class Carillon_Bell(TimeStampedModel):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    carillon = models.ForeignKey(Carillon, on_delete=models.CASCADE, related_name='bell_links')
    bell = models.ForeignKey(Bell, on_delete=models.CASCADE, related_name='carillon_links')
    start_date = models.DateField(verbose_name='Startdatum', blank=True, null=True)
    end_date = models.DateField(verbose_name='Einddatum', blank=True, null=True)
    relative_pitch = models.CharField(max_length=25, blank=True, null=True)
    comments = models.TextField(verbose_name='Opmerkingen', blank=True, null=True)

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError('Startdatum kan niet na einddatum zijn')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['carillon', 'bell', 'start_date'], name='uniq_carillon_bell_period')
        ]
        verbose_name = 'Beiaard Klok'
        verbose_name_plural = 'Beiaarden Klokken'

    def __str__(self):
        return f"{self.carillon.tower.name} - {self.bell.name}"


class Bell_Founder(TimeStampedModel):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    bell = models.ForeignKey(Bell, on_delete=models.CASCADE, related_name='founder_links')
    founder = models.ForeignKey(Founder, on_delete=models.CASCADE, related_name='bell_links')
    date_of_work = models.IntegerField(
        verbose_name='Jaar van werken',
        blank=True,
        null=True,
        validators=[MinValueValidator(600), MaxValueValidator(2100)],
        help_text='Jaar waarin het werk werd uitgevoerd'
    )
    type_of_work = models.CharField(
        max_length=100,
        verbose_name='Type van werken',
        blank=True,
        null=True,
        help_text='Bijvoorbeeld: "gieten", "reparatie", "hergieten"'
    )
    is_primary_founder = models.BooleanField(
        verbose_name='Is primaire gieter',
        default=False
    )
    comments = models.TextField(verbose_name='Opmerkingen', blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['bell', 'founder', 'type_of_work', 'date_of_work'], name='uniq_bell_founder_work')
        ]
        verbose_name = 'Klok Gieter'
        verbose_name_plural = 'Klokken Gieters'

    def __str__(self):
        return f"{self.bell.name} - {self.founder.primary_name}"


# ---------------------------------------------------------------------------
# Tester feedback -- lightweight in-site comments attachable to any record.
# ---------------------------------------------------------------------------

class Feedback(TimeStampedModel):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    # Optional link to any object (a specific bell, tower, ...) via the
    # contenttypes framework, or left empty for general/site-wide feedback.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    subject = models.CharField(max_length=200, verbose_name='Onderwerp', blank=True, null=True)
    message = models.TextField(verbose_name='Bericht')
    # Optional so anonymous beta testers can leave a way to be reached.
    contact = models.CharField(
        max_length=200, verbose_name='Naam of e-mail', blank=True, null=True,
        help_text='Optioneel — zodat we kunnen terugkoppelen.'
    )
    # The page the feedback was sent from, captured automatically for context.
    page_url = models.CharField(max_length=300, verbose_name='Pagina', blank=True, null=True)
    is_resolved = models.BooleanField(default=False, verbose_name='Opgelost')

    class Meta:
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedback'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['is_resolved']),
        ]

    def __str__(self):
        return f"{self.subject or 'Feedback'} ({self.created_at:%Y-%m-%d})"
