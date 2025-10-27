from django.contrib import admin
import core.models as models
from django.contrib.admin.sites import AlreadyRegistered


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


class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "address")
    search_fields = ("name", "address", "phone", "email")


class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "venue", "terrainType", "terrainDifficulty")
    inlines = [LocationImageInline]
    search_fields = ("name", "venue__name")


class LocationImageAdmin(admin.ModelAdmin):
    list_display = ("id", "location", "imageUrl", "description")
    search_fields = ("location__name", "description")


class ActivityAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "difficultyLevel")
    inlines = [ActivityImageInline, ActivityEquipmentInlineForActivity]
    search_fields = ("name",)
    list_filter = ("difficultyLevel",)


class ActivityImageAdmin(admin.ModelAdmin):
    list_display = ("id", "activity", "imageUrl", "description")
    search_fields = ("activity__name", "description")


class EquipmentAdmin(admin.ModelAdmin):
    list_display = ("name", "quantityAvailable")
    inlines = [ActivityEquipmentInlineForEquipment]
    search_fields = ("name",)


class ActivityEquipmentAdmin(admin.ModelAdmin):
    list_display = ("activity", "equipment", "quantity_needed")
    search_fields = ("activity__name", "equipment__name")


# Register models with safe AlreadyRegistered handling (use admin classes where defined)
for model, admin_class in (
    (models.Venue, VenueAdmin),
    (models.Location, LocationAdmin),
    (models.LocationImage, LocationImageAdmin),
    (models.Activity, ActivityAdmin),
    (models.ActivityImage, ActivityImageAdmin),
    (models.Equipment, EquipmentAdmin),
    (models.ActivityEquipment, ActivityEquipmentAdmin),
):
    try:
        if admin_class:
            admin.site.register(model, admin_class)
        else:
            admin.site.register(model)
    except AlreadyRegistered:
        # If the model was already registered (e.g. reloading), ignore
        pass
