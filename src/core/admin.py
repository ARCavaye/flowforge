from django.contrib import admin
from django.db.models import Count
import core.models as models
from django.contrib.admin.sites import AlreadyRegistered
from django.utils.html import format_html


# Inline for team members
class TeamMembershipInline(admin.TabularInline):
    model = models.TeamMembership
    extra = 1
    fields = ("user", "role")
    raw_id_fields = ("user",)


# Admin helper for Team-owned objects
class TeamOwnedAdmin(admin.ModelAdmin):
    raw_id_fields = ("owner_team",)
    list_filter = ("owner_team",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "owner_team":
            kwargs["queryset"] = models.Team.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        """Add select_related for owner_team to avoid N+1 queries"""
        return super().get_queryset(request).select_related("owner_team")


# Inlines to show the through-model (activityEquipment) on both Activity and Equipment admin pages
class ActivityEquipmentInlineForActivity(admin.TabularInline):
    model = models.ActivityEquipment
    extra = 0
    fields = ("equipment", "quantity_needed")
    raw_id_fields = ("equipment",)


class ActivityEquipmentInlineForEquipment(admin.TabularInline):
    model = models.ActivityEquipment
    extra = 0
    fields = ("activity", "quantity_needed")
    raw_id_fields = ("activity",)


# Inline to show activity images on Activity admin
class ActivityImageInline(admin.TabularInline):
    model = models.ActivityImage
    extra = 0
    fields = ("imageUrl", "description")
    readonly_fields = ()


# Inline to show location images on Location admin
class LocationImageInline(admin.TabularInline):
    model = models.LocationImage
    extra = 0
    fields = ("imageUrl", "description")
    readonly_fields = ()


class VenueAdmin(TeamOwnedAdmin):
    list_display = ("name", "description", "address", "owner_team")
    search_fields = ("name", "address", "phone", "email")


class LocationAdmin(TeamOwnedAdmin):
    list_display = ("name", "venue", "terrainType", "terrainDifficulty", "owner_team")
    inlines = [LocationImageInline]
    search_fields = ("name", "venue__name")


class LocationImageAdmin(admin.ModelAdmin):
    list_display = ("id", "location", "imageUrl", "description")
    search_fields = ("location__name", "description")


class ActivityAdmin(TeamOwnedAdmin):
    list_display = ("name", "description", "difficultyLevel", "owner_team")
    inlines = [ActivityImageInline, ActivityEquipmentInlineForActivity]
    search_fields = ("name",)
    list_filter = ("difficultyLevel",)


class ActivityImageAdmin(admin.ModelAdmin):
    list_display = ("id", "activity", "imageUrl", "description")
    search_fields = ("activity__name", "description")


class EquipmentAdmin(TeamOwnedAdmin):
    list_display = ("name", "quantityAvailable", "owner_team")
    inlines = [ActivityEquipmentInlineForEquipment]
    search_fields = ("name",)


class ActivityEquipmentAdmin(TeamOwnedAdmin):
    list_display = ("activity", "equipment", "quantity_needed", "owner_team")
    search_fields = ("activity__name", "equipment__name")


class TeamAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "member_count",
        "activities_count",
        "equipment_count",
        "venues_count",
    )
    search_fields = ("name",)
    inlines = [TeamMembershipInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            _member_count=Count("memberships", distinct=True),
            _activities_count=Count("core_activity_owned_objects", distinct=True),
            _equipment_count=Count("core_equipment_owned_objects", distinct=True),
            _venues_count=Count("core_venue_owned_objects", distinct=True),
        )

    def member_count(self, obj):
        return obj._member_count

    member_count.admin_order_field = "_member_count"
    member_count.short_description = "# Members"

    def activities_count(self, obj):
        return obj._activities_count

    activities_count.admin_order_field = "_activities_count"
    activities_count.short_description = "# Activities"

    def equipment_count(self, obj):
        return obj._equipment_count

    equipment_count.admin_order_field = "_equipment_count"
    equipment_count.short_description = "# Equipment"

    def venues_count(self, obj):
        return obj._venues_count

    venues_count.admin_order_field = "_venues_count"
    venues_count.short_description = "# Venues"


class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ("team", "user", "role", "role_permissions")
    search_fields = ("team__name", "user__username")
    list_filter = ("role", "team")

    def role_permissions(self, obj):
        perms = []
        if obj.can_read():
            perms.append("Read")
        if obj.can_write():
            perms.append("Write")
        if obj.can_manage():
            perms.append("Manage")
        return format_html('<span style="color: #666;">{}</span>', ", ".join(perms))

    role_permissions.short_description = "Permissions"


class PlanSectionItemInline(admin.TabularInline):
    model = models.PlanSectionItem
    extra = 1
    fields = ("item_type", "location", "activity", "notes", "duration_minutes", "order")
    raw_id_fields = ("location", "activity")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("location", "activity")


class PlanSectionInline(admin.TabularInline):
    model = models.PlanSection
    extra = 0
    fields = ("name", "order")
    show_change_link = True  # Allows clicking through to edit section items


class PlanAdmin(TeamOwnedAdmin):
    list_display = (
        "venue",
        "session_date",
        "session_time",
        "group_size",
        "ability_level",
        "coaches_required",
        "coach_qualification_required",
        "owner_team",
    )
    list_filter = (
        "venue",
        "ability_level",
        "session_date",
        "coach_qualification_required",
        "owner_team",
    )
    search_fields = ("venue__name", "plan_goal")
    inlines = [PlanSectionInline]
    date_hierarchy = "session_date"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("venue")


class PlanSectionAdmin(admin.ModelAdmin):
    list_display = ("name", "plan", "order")
    list_filter = ("plan__venue", "plan__session_date")
    search_fields = ("name", "plan__venue__name")
    inlines = [PlanSectionItemInline]
    ordering = ["plan", "order"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("plan", "plan__venue")


# Register models with safe AlreadyRegistered handling (use admin classes where defined)
for model, admin_class in (
    (models.Venue, VenueAdmin),
    (models.Location, LocationAdmin),
    (models.LocationImage, LocationImageAdmin),
    (models.Activity, ActivityAdmin),
    (models.ActivityImage, ActivityImageAdmin),
    (models.Equipment, EquipmentAdmin),
    (models.ActivityEquipment, ActivityEquipmentAdmin),
    (models.Team, TeamAdmin),
    (models.TeamMembership, TeamMembershipAdmin),
    (models.Plan, PlanAdmin),
    (models.PlanSection, PlanSectionAdmin),
):
    try:
        if admin_class:
            admin.site.register(model, admin_class)
        else:
            admin.site.register(model)
    except AlreadyRegistered:
        # If the model was already registered (e.g. reloading), ignore
        pass
