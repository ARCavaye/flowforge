from django.db import models
from django.core import validators

# Create your models here.


class Venue(models.Model):
    name = models.CharField(
        max_length=100,
        blank=False,
        unique=True,
        help_text="Name of the venue",
        verbose_name="Venue Name",
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the venue",
        verbose_name="Venue Description",
    )
    address = models.CharField(
        max_length=255,
        blank=False,
        help_text="Physical address of the venue",
        verbose_name="Venue Address",
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        help_text="Contact phone number",
        verbose_name="Contact Phone",
    )
    email = models.EmailField(
        blank=True, help_text="Contact email address", verbose_name="Contact Email"
    )
    riskAssessmentUrl = models.URLField(
        blank=True,
        help_text="URL to the venue's risk assessment document",
        verbose_name="Risk Assessment URL",
    )

    def __str__(self):
        return self.name


class Location(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, verbose_name="Venue")
    name = models.CharField(
        max_length=100,
        blank=False,
        help_text="Name of the location within the venue",
        verbose_name="Location Name",
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the location",
        verbose_name="Location Description",
    )
    coordinates = models.CharField(
        max_length=50,
        blank=True,
        help_text="GPS coordinates of the location",
        verbose_name="Coordinates",
    )
    terrainType = models.CharField(
        max_length=50,
        blank=True,
        help_text="Type of terrain (e.g., paved, gravel, grass)",
        verbose_name="Terrain Type",
    )
    features = models.TextField(
        blank=True,
        help_text="Notable features of the location",
        verbose_name="Features",
    )
    terrainDifficulty = models.IntegerField(
        blank=True,
        null=True,
        default=1,
        help_text="1 (easy) to 5 (hard)",
        validators=[validators.MinValueValidator(1), validators.MaxValueValidator(5)],
        verbose_name="Terrain Difficulty",
    )

    def __str__(self):
        return f"{self.name} at {self.venue.name}"


class LocationImage(models.Model):
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, verbose_name="Location"
    )
    imageUrl = models.ImageField(
        upload_to="location_images/",
        blank=False,
        help_text="Image of the location",
        verbose_name="Image",
    )
    description = models.TextField(blank=True, verbose_name="Description")

    def __str__(self):
        return f"Image for {self.location.name}"


class Activity(models.Model):
    name = models.CharField(
        max_length=100,
        blank=False,
        help_text="Name of the activity",
        verbose_name="Activity Name",
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the activity",
        verbose_name="Activity Description",
    )
    durationMinutes = models.IntegerField(
        blank=True,
        null=True,
        help_text="Estimated duration of the activity in minutes",
        verbose_name="Duration (minutes)",
    )
    difficultyLevel = models.IntegerField(
        blank=True,
        null=True,
        default=1,
        help_text="1 (easy) to 5 (hard)",
        validators=[validators.MinValueValidator(1), validators.MaxValueValidator(5)],
        verbose_name="Difficulty Level",
    )
    coachingPoints = models.TextField(
        blank=True,
        help_text="Key coaching points for the activity",
        verbose_name="Coaching Points",
    )
    safetyConsiderations = models.TextField(
        blank=True,
        help_text="Safety considerations for the activity",
        verbose_name="Safety Considerations",
    )

    def __str__(self):
        return f"{self.name}"


class ActivityImage(models.Model):
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, verbose_name="Activity"
    )
    imageUrl = models.ImageField(
        upload_to="activity_images/",
        blank=False,
        help_text="Image of the activity",
        verbose_name="Image",
    )
    description = models.TextField(
        blank=True, help_text="Description of the image", verbose_name="Description"
    )

    def __str__(self):
        return f"Image for {self.activity.name}"


class Equipment(models.Model):
    name = models.CharField(
        max_length=100,
        blank=False,
        help_text="Name of the equipment",
        verbose_name="Equipment Name",
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the equipment",
        verbose_name="Equipment Description",
    )
    quantityAvailable = models.IntegerField(
        blank=True,
        null=True,
        help_text="Quantity of this equipment available",
        verbose_name="Quantity Available",
    )
    safetyInstructions = models.TextField(
        blank=True,
        help_text="Safety instructions for using the equipment",
        verbose_name="Safety Instructions",
    )
    activities = models.ManyToManyField(
        "activity",
        through="activityEquipment",
        related_name="equipment_items",
        verbose_name="Activities",
    )

    def __str__(self):
        return f"{self.name}"


class ActivityEquipment(models.Model):
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, verbose_name="Activity"
    )
    equipment = models.ForeignKey(
        Equipment, on_delete=models.CASCADE, verbose_name="Equipment"
    )
    quantity_needed = models.PositiveIntegerField(
        default=1,
        help_text="Quantity of this equipment needed for the activity",
        verbose_name="Quantity Needed",
    )

    class Meta:
        unique_together = ["activity", "equipment"]

    def __str__(self):
        return (
            f"{self.quantity_needed} x {self.equipment.name} for {self.activity.name}"
        )
