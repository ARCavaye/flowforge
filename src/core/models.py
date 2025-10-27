from django.db import models
from django.core import validators

# Create your models here.


class venue(models.Model):
    name = models.CharField(
        max_length=100, blank=False, unique=True, help_text="Name of the venue"
    )
    description = models.TextField(
        blank=True, help_text="Detailed description of the venue"
    )
    address = models.CharField(
        max_length=255, blank=False, help_text="Physical address of the venue"
    )
    phone = models.CharField(
        max_length=15, blank=True, help_text="Contact phone number"
    )
    email = models.EmailField(blank=True, help_text="Contact email address")
    riskAssessmentUrl = models.URLField(
        blank=True, help_text="URL to the venue's risk assessment document"
    )

    def __str__(self):
        return self.name


class location(models.Model):
    venue = models.ForeignKey(venue, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=100, blank=False, help_text="Name of the location within the venue"
    )
    description = models.TextField(
        blank=True, help_text="Detailed description of the location"
    )
    coordinates = models.CharField(
        max_length=50, blank=True, help_text="GPS coordinates or map reference"
    )
    terrainType = models.CharField(
        max_length=50,
        blank=True,
        help_text="Type of terrain (e.g., paved, gravel, grass)",
    )
    features = models.TextField(
        blank=True, help_text="Notable features of the location"
    )
    terrainDifficulty = models.IntegerField(
        blank=True,
        null=True,
        default=1,
        help_text="1 (easy) to 5 (hard)",
        validators=[validators.MinValueValidator(1), validators.MaxValueValidator(5)],
    )

    def __str__(self):
        return f"{self.name} at {self.venue.name}"


class locationImage(models.Model):
    location = models.ForeignKey(location, on_delete=models.CASCADE)
    imageUrl = models.ImageField(
        upload_to="location_images/", blank=False, help_text="Image of the location"
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return f"Image for {self.location.name}"
