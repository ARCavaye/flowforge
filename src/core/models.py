from django.db import models
from django.core import validators

# Create your models here.

from django.conf import settings


# Team + membership models
class Team(models.Model):
    name = models.CharField(
        max_length=150, unique=True, help_text="Team name", verbose_name="Team Name"
    )
    description = models.TextField(
        blank=True, help_text="Description of the team", verbose_name="Team Description"
    )

    def __str__(self):
        return self.name


class TeamMembership(models.Model):
    ROLE_SESSION_LEADER = "leader"
    ROLE_SESSION_PLANNER = "planner"
    ROLE_TEAM_MANAGER = "manager"

    ROLE_CHOICES = (
        (ROLE_SESSION_LEADER, "Session Leader"),
        (ROLE_SESSION_PLANNER, "Session Planner"),
        (ROLE_TEAM_MANAGER, "Team Manager"),
    )

    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="memberships", verbose_name="Team"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="team_memberships",
        verbose_name="User",
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_SESSION_LEADER,
        verbose_name="Role",
    )

    class Meta:
        unique_together = ("team", "user")

    def can_read(self):
        return True

    def can_write(self):
        return self.role in (self.ROLE_SESSION_PLANNER, self.ROLE_TEAM_MANAGER)

    def can_manage(self):
        return self.role == self.ROLE_TEAM_MANAGER

    def __str__(self):
        return f"{self.user} as {self.get_role_display()} on {self.team}"


class TeamOwnedMixin(models.Model):
    owner_team = models.ForeignKey(
        Team,
        verbose_name="Owner Team",
        help_text="Team that owns this object",
        related_name="%(app_label)s_%(class)s_owned_objects",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

    def is_team_owner(self, team_or_id):
        if not team_or_id:
            return False
        try:
            tid = team_or_id.id if hasattr(team_or_id, "id") else int(team_or_id)
        except Exception:
            return False
        return self.owner_team_id == tid


# Domain models
class Venue(TeamOwnedMixin, models.Model):
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


class Location(TeamOwnedMixin, models.Model):
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


class LocationImage(TeamOwnedMixin, models.Model):
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


class Activity(TeamOwnedMixin, models.Model):
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


class ActivityImage(TeamOwnedMixin, models.Model):
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


class Equipment(TeamOwnedMixin, models.Model):
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
        "Activity",
        through="ActivityEquipment",
        related_name="equipment_items",
        verbose_name="Activities",
    )

    def __str__(self):
        return f"{self.name}"


class ActivityEquipment(TeamOwnedMixin, models.Model):
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
