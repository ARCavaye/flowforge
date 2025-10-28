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


class Plan(TeamOwnedMixin, models.Model):
    ABILITY_BEGINNER = "beginner"
    ABILITY_INTERMEDIATE = "intermediate"
    ABILITY_ADVANCED = "advanced"
    ABILITY_MIXED = "mixed"

    ABILITY_CHOICES = [
        (ABILITY_BEGINNER, "Beginner"),
        (ABILITY_INTERMEDIATE, "Intermediate"),
        (ABILITY_ADVANCED, "Advanced"),
        (ABILITY_MIXED, "Mixed Abilities"),
    ]

    venue = models.ForeignKey(
        Venue,
        on_delete=models.PROTECT,
        verbose_name="Venue",
        help_text="Where the session will take place",
    )
    session_date = models.DateField(
        verbose_name="Session Date", help_text="Date of the planned session"
    )
    session_time = models.TimeField(
        verbose_name="Session Time", help_text="Start time of the session"
    )
    session_length_minutes = models.PositiveIntegerField(
        verbose_name="Session Length", help_text="Duration of the session in minutes"
    )
    group_size = models.PositiveIntegerField(
        verbose_name="Group Size", help_text="Expected number of participants"
    )
    age_range = models.CharField(
        max_length=50,
        verbose_name="Age Range",
        help_text="Age range of participants (e.g., '8-10', '14+', 'Adult')",
    )
    ability_level = models.CharField(
        max_length=20,
        choices=ABILITY_CHOICES,
        default=ABILITY_MIXED,
        verbose_name="Ability Level",
        help_text="Overall ability level of the group",
    )
    coaches_required = models.PositiveIntegerField(
        verbose_name="Coaches Required",
        help_text="Number of coaches needed for this session",
        default=1,
    )
    # Coach qualification choices (machine-friendly keys stored in DB)
    COACH_QUALIFICATION_CHOICES = [
        ("i2c_bmx_freestyle", "I2C BMX Freestyle"),
        ("i2c_bmx_race", "I2C BMX Race"),
        ("i2c_cycle_speedway", "I2C Cycle Speedway"),
        ("i2c_cycling", "I2C Cycling"),
        ("i2c_off_road", "I2C Off-Road"),
        ("i2c_road", "I2C Road"),
        ("i2c_track", "I2C Track"),
        ("cic_bmx_freestyle", "CIC BMX Freestyle"),
        ("cic_bmx_race", "CIC BMX Race"),
        ("cic_cx", "CIC CX"),
        ("cic_mtb_xc", "CIC MTB XC"),
        ("cic_mtb_gravity", "CIC MTB Gravity"),
        ("cic_road", "CIC Road"),
        ("cic_track", "CIC Track"),
    ]

    coach_qualification_required = models.CharField(
        max_length=50,
        choices=COACH_QUALIFICATION_CHOICES,
        blank=True,
        null=True,
        verbose_name="Coach Qualification Level Required",
        help_text="Required coach qualification for this session (optional)",
    )
    plan_goal = models.TextField(
        verbose_name="Session Goal", help_text="Main objective or goal for this session"
    )

    def __str__(self):
        return (
            f"Plan for {self.venue.name} on {self.session_date} at {self.session_time}"
        )

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            # Create default sections if this is a new plan
            sections = ["Start", "Middle", "End"]
            for i, name in enumerate(sections):
                PlanSection.objects.create(plan=self, name=name, order=i)


class PlanSection(models.Model):
    plan = models.ForeignKey(
        Plan, on_delete=models.CASCADE, related_name="sections", verbose_name="Plan"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Section Name",
        help_text="Name of this section (e.g., 'Warm-up', 'Main Activity', 'Cool Down')",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Order",
        help_text="Order in which this section appears in the plan",
    )

    class Meta:
        ordering = ["order"]
        unique_together = ["plan", "order"]

    def __str__(self):
        return f"{self.name} - {self.plan}"


class PlanSectionItem(models.Model):
    ITEM_TYPE_LOCATION = "location"
    ITEM_TYPE_ACTIVITY = "activity"
    ITEM_TYPE_NOTE = "note"

    ITEM_TYPE_CHOICES = [
        (ITEM_TYPE_LOCATION, "Location"),
        (ITEM_TYPE_ACTIVITY, "Activity"),
        (ITEM_TYPE_NOTE, "Note"),
    ]

    section = models.ForeignKey(
        PlanSection,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Section",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Order",
        help_text="Order in which this item appears in the section",
    )
    item_type = models.CharField(
        max_length=20, choices=ITEM_TYPE_CHOICES, verbose_name="Item Type"
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Location",
    )
    activity = models.ForeignKey(
        Activity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Activity",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notes",
        help_text="Additional notes or free-form content for this item",
    )
    duration_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Duration",
        help_text="Optional duration for this item in minutes",
    )

    class Meta:
        ordering = ["order"]
        unique_together = ["section", "order"]

    def clean(self):
        from django.core.exceptions import ValidationError

        # Ensure only one of location/activity is set based on item_type
        if self.item_type == self.ITEM_TYPE_LOCATION and not self.location:
            raise ValidationError(
                {"location": "Location is required for location type items"}
            )
        if self.item_type == self.ITEM_TYPE_ACTIVITY and not self.activity:
            raise ValidationError(
                {"activity": "Activity is required for activity type items"}
            )
        if self.item_type == self.ITEM_TYPE_NOTE and not self.notes:
            raise ValidationError({"notes": "Notes are required for note type items"})

    def __str__(self):
        if self.item_type == self.ITEM_TYPE_LOCATION:
            return f"Location: {self.location}"
        elif self.item_type == self.ITEM_TYPE_ACTIVITY:
            return f"Activity: {self.activity}"
        else:
            return f"Note: {self.notes[:50]}..."
